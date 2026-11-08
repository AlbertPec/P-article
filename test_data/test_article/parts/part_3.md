##### 2.2.2. Ship speed loss in winds and waves

Additional resistance caused by wind and waves can reduce a vessel's speed below its service speed. This is known as **involuntary speed reduction**. To maintain constant speed in rough weather, the main engine must deliver more power.

The study uses the Kwon method, based on work by Townsin and Kwon, to estimate involuntary speed loss in irregular waves and wind for different sea states.

![Kwon method: speed-loss equations](test-article/images/test-article.pdf-0002-18.png)

![Kwon method: coefficients and relations](test-article/images/test-article.pdf-0002-19.png)

The speed reduction for each sailing leg depends on several factors:

- \(\Delta V_i\): speed loss in sailing leg \(i\);
- \(V_{s,i}\): ship speed under the selected weather conditions;
- \(C_{\beta,i}\): directional speed-reduction coefficient, determined by relative wind direction and Beaufort number;
- \(C_{U,i}\): speed-reduction coefficient related to block coefficient, loading condition and Froude number;
- \(C_{F,i}\): hull-form coefficient, dependent on ship type, Beaufort number and displacement;
- \(Fr_i\): Froude number;
- \(L_{PP}\): length between perpendiculars;
- \(g\): gravitational acceleration.

The directional coefficient is illustrated in Figure 1. The coefficients used by the Kwon method are provided in Tables 1–3.

![Weather direction angle — Figure 1](test-article/images/test-article.pdf-0003-02.png)

**Figure 1.** Weather direction angle.

**Table 1.** Speed-direction reduction coefficient \(C_{\beta,i}\) (Kwon, 2008).

![Table 1](images/table_001.png)

**Table 2.** Speed-reduction coefficient \(C_{U,i}\) (Kwon, 2008).

![Table 2](images/table_002.png)

**Table 3.** Ship-form coefficient \(C_{F,i}\) (Kwon, 2008).

![Table 3](images/table_003.png)

In addition to involuntary speed loss caused by wind and waves, the model considers **voluntary speed reduction** imposed by navigational-safety constraints. In severe conditions, the vessel may need to sail below the speed predicted by the involuntary-loss model.

For Beaufort numbers \(BN \geq 7\), voluntary speed loss is considered important alongside involuntary speed loss. Previous research also indicates that voluntary speed reduction becomes particularly significant when significant wave height \(H_s\) exceeds 3 m.

The safety assessment in this study uses the vessel's synchronous rolling wavelength \(\lambda_{syn,i}\). Under rough-sea conditions, the relationship between this wavelength, the ship's length and the maximum-energy wavelength is used to determine whether speed must be reduced.

![Safety and synchronous-roll equations](test-article/images/test-article.pdf-0003-14.png)

![Safety-related parameters](test-article/images/test-article.pdf-0003-15.png)

Here, \(\lambda_i\) is wavelength, \(\tau_i\) is wave period and \(\lambda_{syn,i}\) is the ship's synchronous rolling wavelength for sailing leg \(i\). The coefficients \(m\) and \(n\) depend on course and Beaufort number, as specified in Table 4.

**Table 4.** Coefficients \(m\) and \(n\) (Aertssen method).

![Table 4](images/table_004.png)