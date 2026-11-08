
import argparse
import os
import re
import shutil
from pathlib import Path

import pymupdf
import pymupdf4llm


# ==================================================
# Konfiguracja
# ==================================================

IMAGE_DPI = 180
TABLE_DPI = 250

TABLE_MARGIN = 3
PICTURE_MARGIN = 1

# Klasy ignorowane podczas generowania Markdown.
IGNORED_CLASSES = {
    "page-header",
    "page-footer",
}

# Klasy, których zawartość zapisujemy jako tekst.
TEXT_CLASSES = {
    "text",
    "section-header",
    "title",
    "caption",
    "list-item",
    "footnote",
    "formula",
}


# ==================================================
# Narzędzia
# ==================================================

def clean_text(text: str) -> str:
    """Czyści fragment tekstu bez niszczenia jego formatowania Markdown."""

    if not text:
        return ""

    text = text.strip()

    # Usunięcie nadmiarowych pustych linii.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def extract_box_text(chunk: dict, box: dict) -> str:
    """Pobiera tekst przypisany do konkretnego page_box."""

    text = chunk.get("text", "")
    pos = box.get("pos")

    if not pos or len(pos) != 2:
        return ""

    start, stop = pos

    if start < 0 or stop < start or stop > len(text):
        return ""

    return clean_text(text[start:stop])


def normalize_image_paths(markdown: str, images_dir: Path) -> str:
    """Zamienia ścieżki obrazów na względne wobec article.md."""

    absolute = str(images_dir.resolve())

    # PyMuPDF4LLM może zapisać ścieżkę względem bieżącego katalogu.
    relative = os.path.relpath(absolute)

    variants = [
        absolute,
        absolute.replace("\\", "/"),
        relative,
        relative.replace("\\", "/"),
    ]

    for path in variants:
        markdown = markdown.replace(path, "images")

    return markdown.replace("\\", "/")


def add_markdown_heading(text: str, level: int) -> str:
    """Zapewnia nagłówkowi odpowiedni poziom Markdown."""

    text = text.strip()

    if not text:
        return ""

    # Jeżeli biblioteka już wygenerowała nagłówek,
    # zachowujemy jego tekst i formatowanie.
    if text.startswith("#"):
        return text

    return f"{'#' * level} {text}"


def add_markdown_image(text: str) -> str:
    """Sprawdza, czy fragment zawiera już odnośnik do obrazu."""

    if not text:
        return ""

    # PyMuPDF4LLM zazwyczaj umieszcza tu gotowy
    # odnośnik Markdown do wyeksportowanego obrazu.
    if re.search(r"!\[[^\]]*\]\([^)]+\)", text):
        return text

    return text


# ==================================================
# Renderowanie obszarów strony
# ==================================================

def get_box_rect(box: dict, page: pymupdf.Page) -> pymupdf.Rect:
    """Pobiera i ogranicza bbox do granic strony."""

    bbox = box.get("bbox")

    if bbox is None:
        raise ValueError("Brak bbox w page_box")

    rect = pymupdf.Rect(bbox)

    rect &= page.rect

    if rect.is_empty or rect.is_infinite:
        raise ValueError(f"Nieprawidłowy bbox: {bbox}")

    return rect


def save_box_image(
    page: pymupdf.Page,
    box: dict,
    output_path: Path,
    dpi: int,
    margin: float = 0,
) -> None:
    """Renderuje wybrany obszar strony do PNG."""

    rect = get_box_rect(box, page)

    if margin:
        rect = pymupdf.Rect(
            rect.x0 - margin,
            rect.y0 - margin,
            rect.x1 + margin,
            rect.y1 + margin,
        ) & page.rect

    scale = dpi / 72

    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(scale, scale),
        clip=rect,
        alpha=False,
    )

    pixmap.save(str(output_path))


# ==================================================
# Obsługa elementów page_boxes
# ==================================================

def process_box(
    page: pymupdf.Page,
    chunk: dict,
    box: dict,
    images_dir: Path,
    counters: dict,
) -> str:
    """Konwertuje pojedynczy element page_boxes na Markdown."""

    box_class = box.get("class", "unknown")

    # Pomijanie nagłówków i stopek.
    if box_class in IGNORED_CLASSES:
        return ""

    text = extract_box_text(chunk, box)

    # ----------------------------------------------
    # Tytuł dokumentu
    # ----------------------------------------------

    if box_class == "title":
        return add_markdown_heading(text, 1)

    # ----------------------------------------------
    # Nagłówek sekcji
    # ----------------------------------------------

    if box_class == "section-header":
        return add_markdown_heading(text, 2)

    # ----------------------------------------------
    # Zwykły tekst, listy, podpisy, wzory
    # ----------------------------------------------

    if box_class in TEXT_CLASSES:
        return text

    # ----------------------------------------------
    # Ilustracje
    # ----------------------------------------------

    if box_class == "picture":

        # Jeśli PyMuPDF4LLM wygenerował już odnośnik
        # do obrazu, korzystamy z niego.
        image_markdown = add_markdown_image(text)

        if image_markdown:
            return image_markdown

        # Awaryjnie renderujemy bbox.
        counters["picture"] += 1

        filename = (
            f"picture_{counters['picture']:03}.png"
        )

        output_path = images_dir / filename

        try:
            save_box_image(
                page=page,
                box=box,
                output_path=output_path,
                dpi=IMAGE_DPI,
                margin=PICTURE_MARGIN,
            )

            return f"![Illustration](images/{filename})"

        except Exception as exc:
            print(f"  [WARN] Nie zapisano ilustracji: {exc}")
            return ""

    # ----------------------------------------------
    # Tabele
    # ----------------------------------------------

    if box_class == "table":

        counters["table"] += 1

        filename = (
            f"table_{counters['table']:03}.png"
        )

        output_path = images_dir / filename

        try:
            save_box_image(
                page=page,
                box=box,
                output_path=output_path,
                dpi=TABLE_DPI,
                margin=TABLE_MARGIN,
            )

            print(f"  [TABLE] Zapisano {filename}")

            return (
                f"![Table {counters['table']}]"
                f"(images/{filename})"
            )

        except Exception as exc:
            print(f"  [WARN] Nie zapisano tabeli: {exc}")
            return text

    # ----------------------------------------------
    # Nieznane klasy
    # ----------------------------------------------

    if text:
        print(
            f"  [INFO] Nieobsługiwana klasa "
            f"'{box_class}' — zachowuję tekst."
        )

    return text


# ==================================================
# Rekonstrukcja strony
# ==================================================

def process_page(
    page: pymupdf.Page,
    chunk: dict,
    images_dir: Path,
    counters: dict,
) -> str:
    """Buduje Markdown strony na podstawie page_boxes."""

    page_boxes = chunk.get("page_boxes")

    if page_boxes is None:
        raise RuntimeError(
            "Brak page_boxes. "
            "Upewnij się, że Layout jest aktywny."
        )

    blocks = []

    print(f"\nStrona {page.number + 1}")

    # page_boxes są już uporządkowane według reading order.
    for box in sorted(
        page_boxes,
        key=lambda item: item.get("index", 0),
    ):

        result = process_box(
            page=page,
            chunk=chunk,
            box=box,
            images_dir=images_dir,
            counters=counters,
        )

        if result:
            blocks.append(result)

    return "\n\n".join(blocks)


# ==================================================
# Łączenie stron
# ==================================================

def join_pages(pages: list[str]) -> str:
    """Łączy strony, zachowując czytelne granice bloków."""

    non_empty_pages = [
        page.strip()
        for page in pages
        if page and page.strip()
    ]

    return "\n\n".join(non_empty_pages)


# ==================================================
# Główna konwersja
# ==================================================

def convert_pdf(input_pdf: Path) -> Path:

    input_pdf = input_pdf.resolve()

    if not input_pdf.exists():
        raise FileNotFoundError(
            f"Nie znaleziono PDF: {input_pdf}"
        )

    if input_pdf.suffix.lower() != ".pdf":
        raise ValueError(
            "Plik wejściowy musi mieć rozszerzenie .pdf"
        )

    # ----------------------------------------------
    # Katalog wynikowy
    # ----------------------------------------------

    output_dir = input_pdf.parent / input_pdf.stem
    images_dir = output_dir / "images"

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------
    # Kopia oryginalnego PDF
    # ----------------------------------------------

    output_pdf = output_dir / input_pdf.name

    if input_pdf != output_pdf.resolve():
        shutil.copy2(input_pdf, output_pdf)

    # ----------------------------------------------
    # Otwarcie dokumentu
    # ----------------------------------------------

    doc = pymupdf.open(str(input_pdf))

    counters = {
        "picture": 0,
        "table": 0,
    }

    try:

        # ------------------------------------------
        # Ekstrakcja z PyMuPDF4LLM
        # ------------------------------------------

        chunks = pymupdf4llm.to_markdown(
            doc,
            write_images=True,
            image_path=str(images_dir),
            image_format="png",
            dpi=IMAGE_DPI,
            page_chunks=True,
            page_separators=False,
            header=False,
            footer=False,
            show_progress=True,
        )

        markdown_pages = []

        # ------------------------------------------
        # Rekonstrukcja dokumentu
        # ------------------------------------------

        for page_index, chunk in enumerate(chunks):

            page = doc[page_index]

            page_markdown = process_page(
                page=page,
                chunk=chunk,
                images_dir=images_dir,
                counters=counters,
            )

            markdown_pages.append(page_markdown)

        # ------------------------------------------
        # Łączenie stron
        # ------------------------------------------

        markdown = join_pages(markdown_pages)

        # ------------------------------------------
        # Normalizacja ścieżek obrazów
        # ------------------------------------------

        markdown = normalize_image_paths(
            markdown,
            images_dir,
        )

        # ------------------------------------------
        # Zapis Markdown
        # ------------------------------------------

        output_md = output_dir / "article.md"

        output_md.write_text(
            markdown,
            encoding="utf-8",
        )

        # ------------------------------------------
        # Podsumowanie
        # ------------------------------------------

        print("\nKonwersja zakończona.")
        print(f"PDF:          {output_pdf}")
        print(f"Markdown:     {output_md}")
        print(f"Images:       {images_dir}")
        print(f"Ilustracje:   {counters['picture']}")
        print(f"Tabele:       {counters['table']}")

        return output_md

    finally:
        doc.close()


# ==================================================
# CLI
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Konwertuje PDF do Markdown "
            "z wykorzystaniem page_boxes i Layout."
        )
    )

    parser.add_argument(
        "pdf",
        type=Path,
        help="Ścieżka do pliku PDF",
    )

    args = parser.parse_args()

    try:
        convert_pdf(args.pdf)

    except Exception as exc:
        parser.exit(
            status=1,
            message=f"\n[BŁĄD] {exc}\n",
        )


if __name__ == "__main__":
    main()
