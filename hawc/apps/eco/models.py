from django.db import models

# choices for field drop down menus (note: some will need to be changed to frontend autocomplete fields)

study_type_choices = (
    ("observationalgradient", "Observational/gradient"),
    ("manipulationexperiment", "Manipulation/experiment"),
    ("simulation", "Simulation"),
    ("meta-analysis", "Meta-analysis"),
    ("review", "Review"),
)
study_setting_choices = (
    ("field", "Field"),
    ("mesocosm", "Mesocosm"),
    ("greenhouse", "Greenhouse"),
    ("laboratory", "Laboratory"),
    ("model", "Model"),
    ("not_applicable", "Not applicable"),
)
country_choices = (
    ("united_states", "United States"),
    ("afghanistan", "Afghanistan"),
    ("albania", "Albania"),
    ("algeria", "Algeria"),
    ("american_somoa", "American Somoa"),
    ("andorra", "Andorra"),
    ("angola", "Angola"),
    ("anguilla", "Anguilla"),
    ("antarctica", "Antarctica"),
    ("antigua_and_barbuda", "Antigua and Barbuda"),
    ("argentina", "Argentina"),
    ("armenia", "Armenia"),
    ("aruba", "Aruba"),
    ("australia", "Australia"),
    ("austria", "Austria"),
    ("azerbaijjan", "Azerbaijjan"),
    ("bahamas", "Bahamas"),
    ("bahrain", "Bahrain"),
    ("bangladesh", "Bangladesh"),
    ("barbados", "Barbados"),
    ("belarus", "Belarus"),
    ("belgium", "Belgium"),
    ("belize", "Belize"),
    ("benin", "Benin"),
    ("bermuda", "Bermuda"),
    ("bhutan", "Bhutan"),
    ("bolivia", "Bolivia"),
    ("bosnia_and_herzegovina", "Bosnia and Herzegovina"),
    ("botswana", "Botswana"),
    ("brazil", "Brazil"),
    ("british_virgin_islands", "British Virgin Islands"),
    ("brunei_darussalam", "Brunei Darussalam"),
    ("bulgaria", "Bulgaria"),
    ("burkina_faso", "Burkina Faso"),
    ("burundi", "Burundi"),
    ("cambodia", "Cambodia"),
    ("cameroon", "Cameroon"),
    ("canada", "Canada"),
    ("cape_verde", "Cape Verde"),
    ("cayman_islands", "Cayman Islands"),
    ("central_african_republic", "Central African Republic"),
    ("chad", "Chad"),
    ("chile", "Chile"),
    ("china", "China"),
    ("colombia", "Colombia"),
    ("comoros", "Comoros"),
    ("congo", "Congo"),
    ("cook_islands", "Cook Islands"),
    ("costa_rica", "Costa Rica"),
    ("cote_divoire", "Cote d'Ivoire"),
    ("croatia", "Croatia"),
    ("cuba", "Cuba"),
    ("cyprus", "Cyprus"),
    ("czech_republic", "Czech Republic"),
    ("democratic_republic_of_congo", "Democratic Republic of Congo"),
    ("denmark", "Denmark"),
    ("djibouti", "Djibouti"),
    ("dominica", "Dominica"),
    ("dominican_republic", "Dominican Republic"),
    ("east_timor", "East Timor"),
    ("ecuador", "Ecuador"),
    ("egypt", "Egypt"),
    ("el_salvador", "El Salvador"),
    ("equatorial_guinea", "Equatorial Guinea"),
    ("eritrea", "Eritrea"),
    ("estonia", "Estonia"),
    ("ethiopia", "Ethiopia"),
    ("falkland_islands", "Falkland Islands"),
    ("faroe_islands", "Faroe Islands"),
    ("fiji", "Fiji"),
    ("finland", "Finland"),
    ("france", "France"),
    ("french_guiana", "French Guiana"),
    ("french_polynesia", "French Polynesia"),
    ("gabon", "Gabon"),
    ("gambia", "Gambia"),
    ("georgia", "Georgia"),
    ("germany", "Germany"),
    ("ghana", "Ghana"),
    ("gibraltar", "Gibraltar"),
    ("greece", "Greece"),
    ("greenland", "Greenland"),
    ("grenada", "Grenada"),
    ("guadeloupe", "Guadeloupe"),
    ("guam", "Guam"),
    ("guatemala", "Guatemala"),
    ("guinea", "Guinea"),
    ("guinea_bissau", "Guinea Bissau"),
    ("guyana", "Guyana"),
    ("haiti", "Haiti"),
    ("honduras", "Honduras"),
    ("hungary", "Hungary"),
    ("iceland", "Iceland"),
    ("india", "India"),
    ("indonesia", "Indonesia"),
    ("iran", "Iran"),
    ("iraq", "Iraq"),
    ("ireland", "Ireland"),
    ("israel", "Israel"),
    ("italy", "Italy"),
    ("jamaica", "Jamaica"),
    ("japan", "Japan"),
    ("jordan", "Jordan"),
    ("kazakhstan", "Kazakhstan"),
    ("kenya", "Kenya"),
    ("kiribati", "Kiribati"),
    ("kuwait", "Kuwait"),
    ("kyrgyzstan", "Kyrgyzstan"),
    ("laos", "Laos"),
    ("latvia", "Latvia"),
    ("lebanon", "Lebanon"),
    ("lesotho", "Lesotho"),
    ("liberia", "Liberia"),
    ("libya", "Libya"),
    ("liechtenstein", "Liechtenstein"),
    ("lithuania", "Lithuania"),
    ("luxembourg", "Luxembourg"),
    ("macau", "Macau"),
    ("macedonia", "Macedonia"),
    ("madagascar", "Madagascar"),
    ("malawi", "Malawi"),
    ("malaysia", "Malaysia"),
    ("maldives", "Maldives"),
    ("mali_", "Mali "),
    ("malta", "Malta"),
    ("marshall_islands", "Marshall Islands"),
    ("martinique", "Martinique"),
    ("mauritania", "Mauritania"),
    ("mauritius", "Mauritius"),
    ("mayotte", "Mayotte"),
    ("mexico", "Mexico"),
    ("micronesia", "Micronesia"),
    ("moldova", "Moldova"),
    ("monaco", "Monaco"),
    ("mongolia", "Mongolia"),
    ("montserrat", "Montserrat"),
    ("morroco", "Morroco"),
    ("mozambique", "Mozambique"),
    ("myanmar", "Myanmar"),
    ("namibia", "Namibia"),
    ("nauru", "Nauru"),
    ("nepal", "Nepal"),
    ("netherlands", "Netherlands"),
    ("netherlands_antilles", "Netherlands Antilles"),
    ("new_caledonia", "New Caledonia"),
    ("new_zealand", "New Zealand"),
    ("nicaragua", "Nicaragua"),
    ("niger", "Niger"),
    ("nigeria", "Nigeria"),
    ("niue", "Niue"),
    ("norfolk_island", "Norfolk Island"),
    ("north_korea", "North Korea"),
    ("northern_mariana_islands", "Northern Mariana Islands"),
    ("norway", "Norway"),
    ("oman", "Oman"),
    ("pakistan", "Pakistan"),
    ("palau", "Palau"),
    ("palestinian_territory", "Palestinian Territory"),
    ("panama", "Panama"),
    ("papua_new_guinea", "Papua New Guinea"),
    ("paraguay", "Paraguay"),
    ("peru_", "Peru "),
    ("philippines", "Philippines"),
    ("pitcairn_islands", "Pitcairn Islands"),
    ("poland", "Poland"),
    ("portugal", "Portugal"),
    ("puerto_rico", "Puerto Rico"),
    ("qatar", "Qatar"),
    ("reunion", "Reunion"),
    ("romania", "Romania"),
    ("russia", "Russia"),
    ("rwanda", "Rwanda"),
    ("saint_helena", "Saint Helena"),
    ("saint_kitts_and_nevis", "Saint Kitts and Nevis"),
    ("saint_lucia", "Saint Lucia"),
    ("saint_pierre_and_miquelon", "Saint Pierre and Miquelon"),
    ("saint_vincent_and_the_grenadines", "Saint Vincent and the Grenadines"),
    ("samoa", "Samoa"),
    ("san_marino", "San Marino"),
    ("sao_tome_and_principe", "Sao Tome and Principe"),
    ("saudi_arabia", "Saudi Arabia"),
    ("senegal", "Senegal"),
    ("seychelles", "Seychelles"),
    ("sierra_leone", "Sierra Leone"),
    ("singapore", "Singapore"),
    ("slovakia", "Slovakia"),
    ("slovenia", "Slovenia"),
    ("soloman_islands", "Soloman Islands"),
    ("somalia", "Somalia"),
    ("south_africa", "South Africa"),
    ("south_korea", "South Korea"),
    ("spain", "Spain"),
    ("sri_lanka", "Sri Lanka"),
    ("sudan", "Sudan"),
    ("suriname", "Suriname"),
    ("swaziland", "Swaziland"),
    ("sweden", "Sweden"),
    ("switzerland", "Switzerland"),
    ("syria", "Syria"),
    ("taiwan", "Taiwan"),
    ("tajikistan", "Tajikistan"),
    ("tanzania", "Tanzania"),
    ("thailand", "Thailand"),
    ("togo", "Togo"),
    ("tokelau", "Tokelau"),
    ("tonga", "Tonga"),
    ("trinidad_and_tobago", "Trinidad and Tobago"),
    ("tunisia", "Tunisia"),
    ("turkey", "Turkey"),
    ("turkmenistan", "Turkmenistan"),
    ("tuvalu", "Tuvalu"),
    ("us_virgin_islands", "US Virgin Islands"),
    ("uganda", "Uganda"),
    ("ukraine", "Ukraine"),
    ("united_arab_emirates", "United Arab Emirates"),
    ("united_kingdom", "United Kingdom"),
    ("uruguay", "Uruguay"),
    ("uzbekistan", "Uzbekistan"),
    ("vanuatu", "Vanuatu"),
    ("vatican_city", "Vatican City"),
    ("venezuela", "Venezuela"),
    ("vietnam", "Vietnam"),
    ("wallis_and_futuna", "Wallis and Futuna"),
    ("western_sahara", "Western Sahara"),
    ("yemen", "Yemen"),
    ("yugoslavia", "Yugoslavia"),
    ("zambia", "Zambia"),
    ("zimbabwe", "Zimbabwe"),
    ("other", "Other"),
)
state_choices = (
    ("alabama", "Alabama"),
    ("alaska", "Alaska"),
    ("arizona", "Arizona"),
    ("arkansas", "Arkansas"),
    ("california", "California"),
    ("connecticut", "Connecticut"),
    ("colorado", "Colorado"),
    ("delaware", "Delaware"),
    ("district_of_columbia", "District of Columbia"),
    ("florida", "Florida"),
    ("georgia", "Georgia"),
    ("hawaii", "Hawaii"),
    ("idaho", "Idaho"),
    ("illinois", "Illinois"),
    ("indiana", "Indiana"),
    ("iowa", "Iowa"),
    ("kansas", "Kansas"),
    ("kentucky", "Kentucky"),
    ("louisiana", "Louisiana"),
    ("maine", "Maine"),
    ("maryland", "Maryland"),
    ("massachusetts", "Massachusetts"),
    ("michigan", "Michigan"),
    ("minnesota", "Minnesota"),
    ("mississippi", "Mississippi"),
    ("missouri", "Missouri"),
    ("montana", "Montana"),
    ("nebraska", "Nebraska"),
    ("nevada", "Nevada"),
    ("new_hampshire", "New Hampshire"),
    ("new_jersey", "New Jersey"),
    ("new_mexico", "New Mexico"),
    ("new_york", "New York"),
    ("north_carolina", "North Carolina"),
    ("north_dakota", "North Dakota"),
    ("ohio", "Ohio"),
    ("oklahoma", "Oklahoma"),
    ("oregon", "Oregon"),
    ("pennsylvania", "Pennsylvania"),
    ("rhode_island", "Rhode Island"),
    ("south_carolina", "South Carolina"),
    ("south_dakota", "South Dakota"),
    ("tennessee", "Tennessee"),
    ("texas", "Texas"),
    ("utah", "Utah"),
    ("vermont", "Vermont"),
    ("virginia", "Virginia"),
    ("washington", "Washington"),
    ("west_virginia", "West Virginia"),
    ("wisconsin", "Wisconsin"),
    ("wyoming", "Wyoming"),
)
ecoregion_choices = (
    ("1_coast_range", "1. Coast Range"),
    ("2_puget_lowland", "2. Puget Lowland"),
    ("3_willamette_valley", "3. Willamette Valley"),
    ("4_cascades", "4. Cascades"),
    ("5_sierra_nevada", "5. Sierra Nevada"),
    (
        "6_central_california_foothills_and_coastal_mountains",
        "6. Central California Foothills and Coastal Mountains",
    ),
    ("7_central_california_valley", "7. Central California Valley"),
    ("8_southern_california_mountains", "8. Southern California Mountains"),
    ("9_eastern_cascades_slopes_and_foothills", "9. Eastern Cascades Slopes and Foothills"),
    ("10_columbia_plateau", "10. Columbia Plateau"),
    ("11_blue_mountains", "11. Blue Mountains"),
    ("12_snake_river_plain", "12. Snake River Plain"),
    ("13_central_basin_and_range", "13. Central Basin and Range"),
    ("14_mojave_basin_and_range", "14. Mojave Basin and Range"),
    ("15_northern_rockies", "15. Northern Rockies"),
    ("16_idaho_batholith", "16. Idaho Batholith"),
    ("17_middle_rockies", "17. Middle Rockies"),
    ("18_wyoming_basin", "18. Wyoming Basin"),
    ("19_wasatch_and_uinta_mountains", "19. Wasatch and Uinta Mountains"),
    ("20_colorado_plateaus", "20. Colorado Plateaus"),
    ("21_southern_rockies", "21. Southern Rockies"),
    ("22_arizonanew_mexico_plateau", "22. Arizona/New Mexico Plateau"),
    ("23_arizonanew_mexico_mountains", "23. Arizona/New Mexico Mountains"),
    ("24_chihuahuan_deserts", "24. Chihuahuan Deserts"),
    ("25_high_plains", "25. High Plains"),
    ("26_southwestern_tablelands", "26. Southwestern Tablelands"),
    ("27_central_great_plains", "27. Central Great Plains"),
    ("28_flint_hills", "28. Flint Hills"),
    ("29_cross_timbers", "29. Cross Timbers"),
    ("30_edwards_plateau", "30. Edwards Plateau"),
    ("31_southern_texas_plains", "31. Southern Texas Plains"),
    ("32_texas_blackland_prairies", "32. Texas Blackland Prairies"),
    ("33_east_central_texas_plains", "33. East Central Texas Plains"),
    ("34_western_gulf_coastal_plain", "34. Western Gulf Coastal Plain"),
    ("35_south_central_plains", "35. South Central Plains"),
    ("36_ouachita_mountains", "36. Ouachita Mountains"),
    ("37_arkansas_valley", "37. Arkansas Valley"),
    ("38_boston_mountains", "38. Boston Mountains"),
    ("39_ozark_highlands", "39. Ozark Highlands"),
    ("40_central_irregular_plains", "40. Central Irregular Plains"),
    ("41_canadian_rockies", "41. Canadian Rockies"),
    ("42_northwestern_glaciated_plains", "42. Northwestern Glaciated Plains"),
    ("43_northwestern_great_plains", "43. Northwestern Great Plains"),
    ("44_nebraska_sand_hills", "44. Nebraska Sand Hills"),
    ("45_piedmont", "45. Piedmont"),
    ("46_northern_glaciated_plains", "46. Northern Glaciated Plains"),
    ("47_western_corn_belt_plains", "47. Western Corn Belt Plains"),
    ("48_lake_agassiz_plain", "48. Lake Agassiz Plain"),
    ("49_northern_minnesota_wetlands", "49. Northern Minnesota Wetlands"),
    ("50_northern_lakes_and_forests", "50. Northern Lakes and Forests"),
    ("51_north_central_hardwood_forests", "51. North Central Hardwood Forests"),
    ("52_driftless_area", "52. Driftless Area"),
    ("53_southeastern_wisconsin_till_plains", "53. Southeastern Wisconsin Till Plains"),
    ("54_central_corn_belt_plains", "54. Central Corn Belt Plains"),
    ("55_eastern_corn_belt_plains", "55. Eastern Corn Belt Plains"),
    (
        "56_southern_michigannorthern_indiana_drift_plains",
        "56. Southern Michigan/Northern Indiana Drift Plains",
    ),
    ("57_huronerie_lake_plains", "57. Huron/Erie Lake Plains"),
    ("58_northeastern_highlands", "58. Northeastern Highlands"),
    ("59_northeastern_coastal_zone", "59. Northeastern Coastal Zone"),
    ("60_northern_allegheny_plateau", "60. Northern Allegheny Plateau"),
    ("61_erie_drift_plain", "61. Erie Drift Plain"),
    ("62_north_central_appalachians", "62. North Central Appalachians"),
    ("63_middle_atlantic_coastal_plain", "63. Middle Atlantic Coastal Plain"),
    ("64_northern_piedmont", "64. Northern Piedmont"),
    ("65_southeastern_plains", "65. Southeastern Plains"),
    ("66_blue_ridge", "66. Blue Ridge"),
    ("67_ridge_and_valley", "67. Ridge and Valley"),
    ("68_southwestern_appalachians", "68. Southwestern Appalachians"),
    ("69_central_appalachians", "69. Central Appalachians"),
    ("70_western_allegheny_plateau", "70. Western Allegheny Plateau"),
    ("71_interior_plateau", "71. Interior Plateau"),
    ("72_interior_river_valleys_and_hills", "72. Interior River Valleys and Hills"),
    ("73_mississippi_alluvial_plain", "73. Mississippi Alluvial Plain"),
    ("74_mississippi_valley_loess_plains", "74. Mississippi Valley Loess Plains"),
    ("75_southern_coastal_plain", "75. Southern Coastal Plain"),
    ("76_southern_florida_coastal_plain", "76. Southern Florida Coastal Plain"),
    ("77_north_cascades", "77. North Cascades"),
    (
        "78_klamath_mountainscalifornia_high_north_coast_range",
        "78. Klamath Mountains/California High North Coast Range",
    ),
    ("79_madrean_archipelago", "79. Madrean Archipelago"),
    ("80_northern_basin_and_range", "80. Northern Basin and Range"),
    ("81_sonoran_basin_and_range", "81. Sonoran Basin and Range"),
    ("82_acadian_plains_and_hills", "82. Acadian Plains and Hills"),
    ("83_eastern_great_lakes_lowlands", "83. Eastern Great Lakes Lowlands"),
    ("84_atlantic_coastal_pine_barrens", "84. Atlantic Coastal Pine Barrens"),
    ("85_southern_californianorthern_baja_coast", "85. Southern California/Northern Baja Coast"),
)
habitat_choices = (
    ("terrestrial", "Terrestrial"),
    ("riparian", "Riparian"),
    ("freshwater_aquatic", "Freshwater aquatic"),
    ("estuarine", "Estuarine"),
    ("marine", "Marine"),
)
habitat_terrestrial_choices = (
    ("forest", "Forest"),
    ("grassland", "Grassland"),
    ("desert", "Desert"),
    ("heathland", "Heathland"),
    ("agricultural", "Agricultural"),
    ("urbansuburban", "Urban/suburban"),
    ("tundra", "Tundra"),
)
habitat_aquatic_freshwater_choices = (
    ("streamriver", "Stream/river"),
    ("wetland", "Wetland"),
    ("lakereservoir", "Lake/reservoir"),
)
climate_choices = (
    ("temperate", "Temperate"),
    ("tropicalsubtropical", "Tropical/subtropical"),
    ("dry", "Dry"),
    ("arcticsubarctic", "Arctic/subarctic"),
    ("alpine", "Alpine"),
    ("not_specified", "Not specified"),
)
cause_term_choices = (("tbd", "TBD"),)
cause_measure_choices = (("tbd", "TBD"),)
cause_bio_org_choices = (
    ("ecosystem", "Ecosystem"),
    ("community", "Community"),
    ("population", "Population"),
    ("individual_organism", "Individual organism"),
    ("sub-organismal", "Sub-organismal"),
)
cause_trajectory_choices = (
    ("increase", "Increase"),
    ("decrease", "Decrease"),
    ("change", "Change"),
    ("other", "Other"),
)
effect_term_choices = (("tbd", "TBD"),)
effect_measure_choices = (("tbd", "TBD"),)
effect_bio_org_choices = (
    ("ecosystem", "Ecosystem"),
    ("community", "Community"),
    ("population", "Population"),
    ("individual_organism", "Individual organism"),
    ("sub-organismal", "Sub-organismal"),
)
effect_trajectory_choices = (
    ("increase", "Increase"),
    ("decrease", "Decrease"),
    ("change", "Change"),
    ("no_change", "No change"),
    ("other", "Other"),
)

modifying_factors_choices = (("tbd", "TBD"),)
response_measure_type_choices = (
    ("correlation_coefficient", "Correlation coefficient"),
    ("r-squared", "R-squared"),
    ("mean_difference", "Mean difference"),
    ("anovapermanova", "ANOVA/PERMANOVA"),
    ("ratio", "Ratio"),
    ("slope_coefficient_beta", "Slope coefficient (beta)"),
    ("ordination", "Ordination"),
    ("threshold", "Threshold"),
)
response_measure_type_correlation_choices = (
    ("pearson", "Pearson"),
    ("spearman", "Spearman"),
    ("not_specified", "Not specified"),
)
response_measure_type_rsq_choices = (
    ("simple_linear", "Simple linear"),
    ("partial", "Partial"),
    ("multiple", "Multiple"),
    ("quantile", "Quantile"),
    ("not_specified", "Not specified"),
)
response_measure_type_ratio_choices = (
    ("response_ratio", "Response ratio"),
    ("odds_ratio", "Odds ratio"),
    ("risk_ratio", "Risk ratio"),
    ("hazard_ratio", "Hazard ratio"),
    ("not_specified", "Not specified"),
)
response_measure_type_meandiff_choices = (
    ("non-standardized", "Non-standardized"),
    ("standardized", "Standardized"),
    ("not_specified", "Not specified"),
)
response_measure_type_slope_choices = (
    ("non-transformed_data", "Non-transformed data"),
    ("transformed_data", "Transformed data"),
    ("not_specified", "Not specified"),
)
response_measure_type_ord_choices = (
    ("canonical_correspondence_analysis_cca", "Canonical correspondence analysis (CCA)"),
    ("principal_components_analysis_pca", "Principal components analysis (PCA)"),
    ("multiple_discriminant_analysis_mda", "Multiple discriminant analysis (MDA)"),
    ("non-multidimensional_scaling_nmds", "Non-multidimensional scaling (NMDS)"),
    ("factor_analysis", "Factor analysis"),
    ("not_specified", "Not specified"),
)
response_measure_type_thresh_choices = (
    ("regression_tree", "Regression tree"),
    ("random_forest", "Random forest"),
    ("breakpoint_piecewise_regression", "Breakpoint (piecewise) regression"),
    ("quantile_regression", "Quantile regression"),
    ("cumulative_frequency_distribution", "Cumulative frequency distribution"),
    ("gradient_forest_analysis", "Gradient forest analysis"),
    ("non-linear_curve_fitting", "Non-linear curve fitting"),
    ("ordination", "Ordination"),
    ("titan", "TITAN"),
    ("not_specified", "Not specified"),
)
response_variability_choices = (
    ("95_ci", "95% CI"),
    ("90_ci", "90% CI"),
    ("standard_deviation", "Standard deviation"),
    ("standard_error", "Standard error"),
    ("not_applicable", "Not applicable"),
)
statistical_sig_measure_type_choices = (
    ("p-value", "P-value"),
    ("f_statistic", "F statistic"),
    ("chi_square", "Chi square"),
    ("not_applicable", "Not applicable"),
)
sort_choices = (("tbd", "TBD"),)

# pick one or many field models are below


class Country(models.Model):

    country = models.CharField(
        verbose_name="Country",
        max_length=100,
        choices=country_choices,
        help_text="Select one or more countries",
    )

    def __str__(self):

        return self.country

    class Meta:
        verbose_name = "Country"


class State(models.Model):

    state = models.CharField(
        verbose_name="State",
        max_length=100,
        choices=state_choices,
        blank=True,
        help_text="Select one or more states, if applicable",
    )

    def __str__(self):

        return self.state

    class Meta:
        verbose_name = "State"


class Climate(models.Model):

    climate = models.CharField(
        verbose_name="Climate",
        max_length=100,
        choices=climate_choices,
        blank=True,
        help_text="Select one or more climates to which the evidence applies",
    )

    def __str__(self):

        return self.climate

    class Meta:
        verbose_name = "Climate"


class Ecoregion(models.Model):

    ecoregion = models.CharField(
        verbose_name="Ecoregion",
        max_length=100,
        choices=ecoregion_choices,
        blank=True,
        help_text="Select one or more Level III Ecoregions, if known",
    )

    def __str__(self):

        return self.ecoregion

    class Meta:
        verbose_name = "Ecoregion"


class Reference(models.Model):

    reference = models.CharField(max_length=100, help_text="Enter a Reference ID!")

    def __str__(self):

        return self.reference

    class Meta:
        verbose_name = "Reference"


class Metadata(models.Model):

    study_id = models.OneToOneField(Reference, on_delete=models.CASCADE)

    study_type = models.CharField(
        max_length=100, choices=study_type_choices, help_text="Select the type of study"
    )

    study_setting = models.CharField(
        max_length=100,
        choices=study_setting_choices,
        help_text="Select the setting in which evidence was generated",
    )

    country = models.ManyToManyField(Country, help_text="Select one or more countries")

    state = models.ManyToManyField(
        State, blank=True, help_text="Select one or more states, if applicable."
    )

    ecoregion = models.ManyToManyField(
        Ecoregion, blank=True, help_text="Select one or more Level III Ecoregions, if known",
    )

    habitat = models.CharField(
        verbose_name="Habitat",
        max_length=100,
        choices=habitat_choices,
        blank=True,
        help_text="Select the habitat to which the evidence applies",
    )

    habitat_terrestrial = models.CharField(
        verbose_name="Terrestrial habitat",
        max_length=100,
        choices=habitat_terrestrial_choices,
        blank=True,
        help_text="If you selected terrestrial, pick the type of terrestrial habitat",
    )

    habitat_aquatic_freshwater = models.CharField(
        verbose_name="Freshwater habitat",
        max_length=100,
        choices=habitat_aquatic_freshwater_choices,
        blank=True,
        help_text="If you selected freshwater, pick the type of freshwater habitat",
    )

    habitat_as_reported = models.TextField(
        verbose_name="Habitat as reported",
        blank=True,
        help_text="Copy and paste 1-2 sentences from article",
    )

    climate = models.ManyToManyField(
        Climate, blank=True, help_text="Select one or more climates to which the evidence applies",
    )

    climate_as_reported = models.TextField(
        verbose_name="Climate as reported", blank=True, help_text="Copy and paste from article",
    )

    def __str__(self):

        return self.study_type

    class Meta:
        verbose_name = "Metadata"


class Cause(models.Model):

    study_id = models.ForeignKey(Reference, on_delete=models.CASCADE)

    term = models.CharField(
        verbose_name="Cause term", max_length=100, choices=cause_term_choices
    )  # autocomplete

    measure = models.CharField(
        verbose_name="Cause measure", max_length=100, choices=cause_measure_choices
    )  # autocomplete

    measure_detail = models.TextField(verbose_name="Cause measure detail", blank=True)

    species = models.CharField(
        verbose_name="Cause species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )

    units = models.CharField(
        verbose_name="Cause units",
        max_length=100,
        help_text="Type the unit associated with the cause term",
    )  # autocomplete?

    bio_org = models.CharField(
        verbose_name="Level of biological organization",
        max_length=100,
        help_text="Select the level of biological organization associated with the cause, if applicable",
        blank=True,
        choices=cause_bio_org_choices,
    )

    trajectory = models.CharField(
        verbose_name="Cause trajectory",
        max_length=100,
        choices=cause_trajectory_choices,
        help_text="Select qualitative description of how the cause measure changes, if applicable",
    )  # autocomplete

    comment = models.TextField(
        verbose_name="Cause comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )

    as_reported = models.TextField(
        verbose_name="Cause as reported", help_text="Copy and paste 1-2 sentences from article",
    )

    def __str__(self):

        return self.term

    class Meta:
        verbose_name = "Cause/Treatment"


class Effect(models.Model):

    cause = models.OneToOneField(Cause, on_delete=models.CASCADE)

    term = models.CharField(verbose_name="Effect term", max_length=100, choices=effect_term_choices)

    measure = models.CharField(
        verbose_name="Effect measure", max_length=100, choices=effect_measure_choices
    )  # autocomplete

    measure_detail = models.CharField(
        verbose_name="Effect measure detail", max_length=100, blank=True
    )  # autocomplete

    species = models.CharField(
        verbose_name="Effect species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )

    units = models.CharField(
        verbose_name="Effect units",
        max_length=100,
        help_text="Type the unit associated with the effect term",
    )  # autocomplete

    bio_org = models.CharField(
        verbose_name="Level of biological organization",
        max_length=100,
        help_text="Select the level of biological organization associated with the cause, if applicable",
        blank=True,
        choices=effect_bio_org_choices,
    )

    trajectory = models.CharField(
        verbose_name="Effect trajectory",
        max_length=100,
        choices=effect_trajectory_choices,
        help_text="Select qualitative description of how the effect measure changes in response to the cause trajectory, if applicable",
    )

    comment = models.TextField(
        verbose_name="Effect comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )

    as_reported = models.TextField(
        verbose_name="Effect as reported", help_text="Copy and paste 1-2 sentences from article",
    )

    modifying_factors = models.CharField(
        verbose_name="Modifying factors",
        max_length=100,
        help_text="Type one or more factors that affect the relationship between the cause and effect",
    )  # autocomplete

    sort = models.CharField(
        verbose_name="Sort quantitative responses",
        max_length=100,
        choices=sort_choices,
        help_text="how do you want to sort multiple quantitative responses?",
        blank=True,
    )

    def __str__(self):

        return self.term

    class Meta:
        verbose_name = "Effect/Response"


class Quantitative(models.Model):

    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)

    cause_level = models.CharField(
        verbose_name="Cause treatment level",
        max_length=100,
        blank=True,
        help_text="Type the specific treatment/exposure/dose level of the cause measure",
    )

    cause_level_value = models.FloatField(
        verbose_name="Cause treatment level value",
        blank=True,
        help_text="Type the numeric value of the specific treatment/exposure/dose level of the cause measure",
        null=True,
    )

    cause_level_units = models.CharField(
        verbose_name="Cause treatment level units",
        max_length=100,
        blank=True,
        help_text="Enter the units of the specific treatment/exposure/dose level of the cause measure",
    )

    sample_size = models.IntegerField(
        verbose_name="Sample size",
        blank=True,
        help_text="Type the number of samples used to calculate the response measure value, if known",
        null=True,
    )

    measure_type_filter = models.CharField(
        verbose_name="Response measure type (filter)",
        max_length=100,
        blank=True,
        choices=response_measure_type_choices,
        help_text="This drop down will filter the following field",
    )

    measure_type = models.CharField(
        verbose_name="Response measure type",
        max_length=40,
        choices=response_measure_type_correlation_choices
        + response_measure_type_rsq_choices
        + response_measure_type_ratio_choices
        + response_measure_type_meandiff_choices
        + response_measure_type_slope_choices
        + response_measure_type_ord_choices
        + response_measure_type_thresh_choices,
        blank=True,
        help_text="Select one response measure type",
    )  # dependent on selection in response measure type column

    measure_value = models.FloatField(
        verbose_name="Response measure value",
        blank=True,
        help_text="Type the numerical value of the response measure",
        null=True,
    )

    description = models.TextField(
        verbose_name="Response measure description",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )

    variability = models.CharField(
        verbose_name="Response variability",
        blank=True,
        max_length=100,
        choices=response_variability_choices,
        help_text="Select how variability in the response measure was reported, if applicable",
    )

    low_variability = models.FloatField(
        verbose_name="Lower response variability measure",
        blank=True,
        help_text="Type the lower numerical bound of the response variability",
        null=True,
    )

    upper_variability = models.FloatField(
        verbose_name="Upper response variability measure",
        blank=True,
        help_text="Type the upper numerical bound of the response variability",
        null=True,
    )

    statistical_sig_type = models.CharField(
        verbose_name="Statistical significance measure type",
        blank=True,
        max_length=100,
        choices=statistical_sig_measure_type_choices,
        help_text="Select the type of statistical significance measure reported",
    )

    statistical_sig_value = models.FloatField(
        verbose_name="Statistical significance measure value",
        blank=True,
        help_text="Type the numerical value of the statistical significance",
        null=True,
    )

    derived_value = models.FloatField(
        verbose_name="Derived response measure value",
        blank=True,
        help_text="Calculation from 'response measure value' based on a formula linked to 'response measure type', if applicable",
        null=True,
    )

    # def __str__(self):

    #    return self.cause_level

    class Meta:
        verbose_name = "Quantitative response information"
