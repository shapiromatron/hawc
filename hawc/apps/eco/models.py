from django.db import models

study_type_choices = (
    ("Observational/gradient", "Observational/gradient"),
    ("Manipulation/experiment", "Manipulation/experiment"),
    ("Simulation", "Simulation"),
    ("Meta-analysis", "Meta-analysis"),
    ("Review", "Review"),
)
study_setting_choices = (
    ("Field", "Field"),
    ("Mesocosm", "Mesocosm"),
    ("Greenhouse", "Greenhouse"),
    ("Laboratory", "Laboratory"),
    ("Model", "Model"),
    ("Not applicable", "Not applicable"),
)
country_choices = (
    ("United States", "United States"),
    ("Afghanistan", "Afghanistan"),
    ("Albania", "Albania"),
    ("Algeria", "Algeria"),
    ("American Somoa", "American Somoa"),
    ("Andorra", "Andorra"),
    ("Angola", "Angola"),
    ("Anguilla", "Anguilla"),
    ("Antarctica", "Antarctica"),
    ("Antigua and Barbuda", "Antigua and Barbuda"),
    ("Argentina", "Argentina"),
    ("Armenia", "Armenia"),
    ("Aruba", "Aruba"),
    ("Australia", "Australia"),
    ("Austria", "Austria"),
    ("Azerbaijjan", "Azerbaijjan"),
    ("Bahamas", "Bahamas"),
    ("Bahrain", "Bahrain"),
    ("Bangladesh", "Bangladesh"),
    ("Barbados", "Barbados"),
    ("Belarus", "Belarus"),
    ("Belgium", "Belgium"),
    ("Belize", "Belize"),
    ("Benin", "Benin"),
    ("Bermuda", "Bermuda"),
    ("Bhutan", "Bhutan"),
    ("Bolivia", "Bolivia"),
    ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
    ("Botswana", "Botswana"),
    ("Brazil", "Brazil"),
    ("British Virgin Islands", "British Virgin Islands"),
    ("Brunei Darussalam", "Brunei Darussalam"),
    ("Bulgaria", "Bulgaria"),
    ("Burkina Faso", "Burkina Faso"),
    ("Burundi", "Burundi"),
    ("Cambodia", "Cambodia"),
    ("Cameroon", "Cameroon"),
    ("Canada", "Canada"),
    ("Cape Verde", "Cape Verde"),
    ("Cayman Islands", "Cayman Islands"),
    ("Central African Republic", "Central African Republic"),
    ("Chad", "Chad"),
    ("Chile", "Chile"),
    ("China", "China"),
    ("Colombia", "Colombia"),
    ("Comoros", "Comoros"),
    ("Congo", "Congo"),
    ("Cook Islands", "Cook Islands"),
    ("Costa Rica", "Costa Rica"),
    ("Cote d'Ivoire", "Cote d'Ivoire"),
    ("Croatia", "Croatia"),
    ("Cuba", "Cuba"),
    ("Cyprus", "Cyprus"),
    ("Czech Republic", "Czech Republic"),
    ("Democratic Republic of Congo", "Democratic Republic of Congo"),
    ("Denmark", "Denmark"),
    ("Djibouti", "Djibouti"),
    ("Dominica", "Dominica"),
    ("Dominican Republic", "Dominican Republic"),
    ("East Timor", "East Timor"),
    ("Ecuador", "Ecuador"),
    ("Egypt", "Egypt"),
    ("El Salvador", "El Salvador"),
    ("Equatorial Guinea", "Equatorial Guinea"),
    ("Eritrea", "Eritrea"),
    ("Estonia", "Estonia"),
    ("Ethiopia", "Ethiopia"),
    ("Falkland Islands", "Falkland Islands"),
    ("Faroe Islands", "Faroe Islands"),
    ("Fiji", "Fiji"),
    ("Finland", "Finland"),
    ("France", "France"),
    ("French Guiana", "French Guiana"),
    ("French Polynesia", "French Polynesia"),
    ("Gabon", "Gabon"),
    ("Gambia", "Gambia"),
    ("Georgia", "Georgia"),
    ("Germany", "Germany"),
    ("Ghana", "Ghana"),
    ("Gibraltar", "Gibraltar"),
    ("Greece", "Greece"),
    ("Greenland", "Greenland"),
    ("Grenada", "Grenada"),
    ("Guadeloupe", "Guadeloupe"),
    ("Guam", "Guam"),
    ("Guatemala", "Guatemala"),
    ("Guinea", "Guinea"),
    ("Guinea Bissau", "Guinea Bissau"),
    ("Guyana", "Guyana"),
    ("Haiti", "Haiti"),
    ("Honduras", "Honduras"),
    ("Hungary", "Hungary"),
    ("Iceland", "Iceland"),
    ("India", "India"),
    ("Indonesia", "Indonesia"),
    ("Iran", "Iran"),
    ("Iraq", "Iraq"),
    ("Ireland", "Ireland"),
    ("Israel", "Israel"),
    ("Italy", "Italy"),
    ("Jamaica", "Jamaica"),
    ("Japan", "Japan"),
    ("Jordan", "Jordan"),
    ("Kazakhstan", "Kazakhstan"),
    ("Kenya", "Kenya"),
    ("Kiribati", "Kiribati"),
    ("Kuwait", "Kuwait"),
    ("Kyrgyzstan", "Kyrgyzstan"),
    ("Laos", "Laos"),
    ("Latvia", "Latvia"),
    ("Lebanon", "Lebanon"),
    ("Lesotho", "Lesotho"),
    ("Liberia", "Liberia"),
    ("Libya", "Libya"),
    ("Liechtenstein", "Liechtenstein"),
    ("Lithuania", "Lithuania"),
    ("Luxembourg", "Luxembourg"),
    ("Macau", "Macau"),
    ("Macedonia", "Macedonia"),
    ("Madagascar", "Madagascar"),
    ("Malawi", "Malawi"),
    ("Malaysia", "Malaysia"),
    ("Maldives", "Maldives"),
    ("Mali ", "Mali "),
    ("Malta", "Malta"),
    ("Marshall Islands", "Marshall Islands"),
    ("Martinique", "Martinique"),
    ("Mauritania", "Mauritania"),
    ("Mauritius", "Mauritius"),
    ("Mayotte", "Mayotte"),
    ("Mexico", "Mexico"),
    ("Micronesia", "Micronesia"),
    ("Moldova", "Moldova"),
    ("Monaco", "Monaco"),
    ("Mongolia", "Mongolia"),
    ("Montserrat", "Montserrat"),
    ("Morroco", "Morroco"),
    ("Mozambique", "Mozambique"),
    ("Myanmar", "Myanmar"),
    ("Namibia", "Namibia"),
    ("Nauru", "Nauru"),
    ("Nepal", "Nepal"),
    ("Netherlands", "Netherlands"),
    ("Netherlands Antilles", "Netherlands Antilles"),
    ("New Caledonia", "New Caledonia"),
    ("New Zealand", "New Zealand"),
    ("Nicaragua", "Nicaragua"),
    ("Niger", "Niger"),
    ("Nigeria", "Nigeria"),
    ("Niue", "Niue"),
    ("Norfolk Island", "Norfolk Island"),
    ("North Korea", "North Korea"),
    ("Northern Mariana Islands", "Northern Mariana Islands"),
    ("Norway", "Norway"),
    ("Oman", "Oman"),
    ("Pakistan", "Pakistan"),
    ("Palau", "Palau"),
    ("Palestinian Territory", "Palestinian Territory"),
    ("Panama", "Panama"),
    ("Papua New Guinea", "Papua New Guinea"),
    ("Paraguay", "Paraguay"),
    ("Peru ", "Peru "),
    ("Philippines", "Philippines"),
    ("Pitcairn Islands", "Pitcairn Islands"),
    ("Poland", "Poland"),
    ("Portugal", "Portugal"),
    ("Puerto Rico", "Puerto Rico"),
    ("Qatar", "Qatar"),
    ("Reunion", "Reunion"),
    ("Romania", "Romania"),
    ("Russia", "Russia"),
    ("Rwanda", "Rwanda"),
    ("Saint Helena", "Saint Helena"),
    ("Saint Kitts and Nevis", "Saint Kitts and Nevis"),
    ("Saint Lucia", "Saint Lucia"),
    ("Saint Pierre and Miquelon", "Saint Pierre and Miquelon"),
    ("Saint Vincent and the Grenadines", "Saint Vincent and the Grenadines"),
    ("Samoa", "Samoa"),
    ("San Marino", "San Marino"),
    ("Sao Tome and Principe", "Sao Tome and Principe"),
    ("Saudi Arabia", "Saudi Arabia"),
    ("Senegal", "Senegal"),
    ("Seychelles", "Seychelles"),
    ("Sierra Leone", "Sierra Leone"),
    ("Singapore", "Singapore"),
    ("Slovakia", "Slovakia"),
    ("Slovenia", "Slovenia"),
    ("Soloman Islands", "Soloman Islands"),
    ("Somalia", "Somalia"),
    ("South Africa", "South Africa"),
    ("South Korea", "South Korea"),
    ("Spain", "Spain"),
    ("Sri Lanka", "Sri Lanka"),
    ("Sudan", "Sudan"),
    ("Suriname", "Suriname"),
    ("Swaziland", "Swaziland"),
    ("Sweden", "Sweden"),
    ("Switzerland", "Switzerland"),
    ("Syria", "Syria"),
    ("Taiwan", "Taiwan"),
    ("Tajikistan", "Tajikistan"),
    ("Tanzania", "Tanzania"),
    ("Thailand", "Thailand"),
    ("Togo", "Togo"),
    ("Tokelau", "Tokelau"),
    ("Tonga", "Tonga"),
    ("Trinidad and Tobago", "Trinidad and Tobago"),
    ("Tunisia", "Tunisia"),
    ("Turkey", "Turkey"),
    ("Turkmenistan", "Turkmenistan"),
    ("Tuvalu", "Tuvalu"),
    ("US Virgin Islands", "US Virgin Islands"),
    ("Uganda", "Uganda"),
    ("Ukraine", "Ukraine"),
    ("United Arab Emirates", "United Arab Emirates"),
    ("United Kingdom", "United Kingdom"),
    ("Uruguay", "Uruguay"),
    ("Uzbekistan", "Uzbekistan"),
    ("Vanuatu", "Vanuatu"),
    ("Vatican City", "Vatican City"),
    ("Venezuela", "Venezuela"),
    ("Vietnam", "Vietnam"),
    ("Wallis and Futuna", "Wallis and Futuna"),
    ("Western Sahara", "Western Sahara"),
    ("Yemen", "Yemen"),
    ("Yugoslavia", "Yugoslavia"),
    ("Zambia", "Zambia"),
    ("Zimbabwe", "Zimbabwe"),
    ("Other", "Other"),
)
state_choices = (
    ("Alabama", "Alabama"),
    ("Alaska", "Alaska"),
    ("Arizona", "Arizona"),
    ("Arkansas", "Arkansas"),
    ("California", "California"),
    ("Connecticut", "Connecticut"),
    ("Colorado", "Colorado"),
    ("Delaware", "Delaware"),
    ("District of Columbia", "District of Columbia"),
    ("Florida", "Florida"),
    ("Georgia", "Georgia"),
    ("Hawaii", "Hawaii"),
    ("Idaho", "Idaho"),
    ("Illinois", "Illinois"),
    ("Indiana", "Indiana"),
    ("Iowa", "Iowa"),
    ("Kansas", "Kansas"),
    ("Kentucky", "Kentucky"),
    ("Louisiana", "Louisiana"),
    ("Maine", "Maine"),
    ("Maryland", "Maryland"),
    ("Massachusetts", "Massachusetts"),
    ("Michigan", "Michigan"),
    ("Minnesota", "Minnesota"),
    ("Mississippi", "Mississippi"),
    ("Missouri", "Missouri"),
    ("Montana", "Montana"),
    ("Nebraska", "Nebraska"),
    ("Nevada", "Nevada"),
    ("New Hampshire", "New Hampshire"),
    ("New Jersey", "New Jersey"),
    ("New Mexico", "New Mexico"),
    ("New York", "New York"),
    ("North Carolina", "North Carolina"),
    ("North Dakota", "North Dakota"),
    ("Ohio", "Ohio"),
    ("Oklahoma", "Oklahoma"),
    ("Oregon", "Oregon"),
    ("Pennsylvania", "Pennsylvania"),
    ("Rhode Island", "Rhode Island"),
    ("South Carolina", "South Carolina"),
    ("South Dakota", "South Dakota"),
    ("Tennessee", "Tennessee"),
    ("Texas", "Texas"),
    ("Utah", "Utah"),
    ("Vermont", "Vermont"),
    ("Virginia", "Virginia"),
    ("Washington", "Washington"),
    ("West Virginia", "West Virginia"),
    ("Wisconsin", "Wisconsin"),
    ("Wyoming", "Wyoming"),
)
ecoregion_choices = (
    ("1. Coast Range", "1. Coast Range"),
    ("2. Puget Lowland", "2. Puget Lowland"),
    ("3. Willamette Valley", "3. Willamette Valley"),
    ("4. Cascades", "4. Cascades"),
    ("5. Sierra Nevada", "5. Sierra Nevada"),
    (
        "6. Central California Foothills and Coastal Mountains",
        "6. Central California Foothills and Coastal Mountains",
    ),
    ("7. Central California Valley", "7. Central California Valley"),
    ("8. Southern California Mountains", "8. Southern California Mountains"),
    ("9. Eastern Cascades Slopes and Foothills", "9. Eastern Cascades Slopes and Foothills"),
    ("10. Columbia Plateau", "10. Columbia Plateau"),
    ("11. Blue Mountains", "11. Blue Mountains"),
    ("12. Snake River Plain", "12. Snake River Plain"),
    ("13. Central Basin and Range", "13. Central Basin and Range"),
    ("14. Mojave Basin and Range", "14. Mojave Basin and Range"),
    ("15. Northern Rockies", "15. Northern Rockies"),
    ("16. Idaho Batholith", "16. Idaho Batholith"),
    ("17. Middle Rockies", "17. Middle Rockies"),
    ("18. Wyoming Basin", "18. Wyoming Basin"),
    ("19. Wasatch and Uinta Mountains", "19. Wasatch and Uinta Mountains"),
    ("20. Colorado Plateaus", "20. Colorado Plateaus"),
    ("21. Southern Rockies", "21. Southern Rockies"),
    ("22. Arizona/New Mexico Plateau", "22. Arizona/New Mexico Plateau"),
    ("23. Arizona/New Mexico Mountains", "23. Arizona/New Mexico Mountains"),
    ("24. Chihuahuan Deserts", "24. Chihuahuan Deserts"),
    ("25. High Plains", "25. High Plains"),
    ("26. Southwestern Tablelands", "26. Southwestern Tablelands"),
    ("27. Central Great Plains", "27. Central Great Plains"),
    ("28. Flint Hills", "28. Flint Hills"),
    ("29. Cross Timbers", "29. Cross Timbers"),
    ("30. Edwards Plateau", "30. Edwards Plateau"),
    ("31. Southern Texas Plains", "31. Southern Texas Plains"),
    ("32. Texas Blackland Prairies", "32. Texas Blackland Prairies"),
    ("33. East Central Texas Plains", "33. East Central Texas Plains"),
    ("34. Western Gulf Coastal Plain", "34. Western Gulf Coastal Plain"),
    ("35. South Central Plains", "35. South Central Plains"),
    ("36. Ouachita Mountains", "36. Ouachita Mountains"),
    ("37. Arkansas Valley", "37. Arkansas Valley"),
    ("38. Boston Mountains", "38. Boston Mountains"),
    ("39. Ozark Highlands", "39. Ozark Highlands"),
    ("40. Central Irregular Plains", "40. Central Irregular Plains"),
    ("41. Canadian Rockies", "41. Canadian Rockies"),
    ("42. Northwestern Glaciated Plains", "42. Northwestern Glaciated Plains"),
    ("43. Northwestern Great Plains", "43. Northwestern Great Plains"),
    ("44. Nebraska Sand Hills", "44. Nebraska Sand Hills"),
    ("45. Piedmont", "45. Piedmont"),
    ("46. Northern Glaciated Plains", "46. Northern Glaciated Plains"),
    ("47. Western Corn Belt Plains", "47. Western Corn Belt Plains"),
    ("48. Lake Agassiz Plain", "48. Lake Agassiz Plain"),
    ("49. Northern Minnesota Wetlands", "49. Northern Minnesota Wetlands"),
    ("50. Northern Lakes and Forests", "50. Northern Lakes and Forests"),
    ("51. North Central Hardwood Forests", "51. North Central Hardwood Forests"),
    ("52. Driftless Area", "52. Driftless Area"),
    ("53. Southeastern Wisconsin Till Plains", "53. Southeastern Wisconsin Till Plains"),
    ("54. Central Corn Belt Plains", "54. Central Corn Belt Plains"),
    ("55. Eastern Corn Belt Plains", "55. Eastern Corn Belt Plains"),
    (
        "56. Southern Michigan/Northern Indiana Drift Plains",
        "56. Southern Michigan/Northern Indiana Drift Plains",
    ),
    ("57. Huron/Erie Lake Plains", "57. Huron/Erie Lake Plains"),
    ("58. Northeastern Highlands", "58. Northeastern Highlands"),
    ("59. Northeastern Coastal Zone", "59. Northeastern Coastal Zone"),
    ("60. Northern Allegheny Plateau", "60. Northern Allegheny Plateau"),
    ("61. Erie Drift Plain", "61. Erie Drift Plain"),
    ("62. North Central Appalachians", "62. North Central Appalachians"),
    ("63. Middle Atlantic Coastal Plain", "63. Middle Atlantic Coastal Plain"),
    ("64. Northern Piedmont", "64. Northern Piedmont"),
    ("65. Southeastern Plains", "65. Southeastern Plains"),
    ("66. Blue Ridge", "66. Blue Ridge"),
    ("67. Ridge and Valley", "67. Ridge and Valley"),
    ("68. Southwestern Appalachians", "68. Southwestern Appalachians"),
    ("69. Central Appalachians", "69. Central Appalachians"),
    ("70. Western Allegheny Plateau", "70. Western Allegheny Plateau"),
    ("71. Interior Plateau", "71. Interior Plateau"),
    ("72. Interior River Valleys and Hills", "72. Interior River Valleys and Hills"),
    ("73. Mississippi Alluvial Plain", "73. Mississippi Alluvial Plain"),
    ("74. Mississippi Valley Loess Plains", "74. Mississippi Valley Loess Plains"),
    ("75. Southern Coastal Plain", "75. Southern Coastal Plain"),
    ("76. Southern Florida Coastal Plain", "76. Southern Florida Coastal Plain"),
    ("77. North Cascades", "77. North Cascades"),
    (
        "78. Klamath Mountains/California High North Coast Range",
        "78. Klamath Mountains/California High North Coast Range",
    ),
    ("79. Madrean Archipelago", "79. Madrean Archipelago"),
    ("80. Northern Basin and Range", "80. Northern Basin and Range"),
    ("81. Sonoran Basin and Range", "81. Sonoran Basin and Range"),
    ("82. Acadian Plains and Hills", "82. Acadian Plains and Hills"),
    ("83. Eastern Great Lakes Lowlands", "83. Eastern Great Lakes Lowlands"),
    ("84. Atlantic Coastal Pine Barrens", "84. Atlantic Coastal Pine Barrens"),
    ("85. Southern California/Northern Baja Coast", "85. Southern California/Northern Baja Coast"),
)
habitat_choices = (
    ("Terrestrial", "Terrestrial"),
    ("Riparian", "Riparian"),
    ("Freshwater aquatic", "Freshwater aquatic"),
    ("Estuarine", "Estuarine"),
    ("Marine", "Marine"),
)
habitat_terrestrial_choices = (
    ("Forest", "Forest"),
    ("Grassland", "Grassland"),
    ("Desert", "Desert"),
    ("Heathland", "Heathland"),
    ("Agricultural", "Agricultural"),
    ("Urban/suburban", "Urban/suburban"),
    ("Tundra", "Tundra"),
)
habitat_aquatic_freshwater_choices = (
    ("Stream/river", "Stream/river"),
    ("Wetland", "Wetland"),
    ("Lake/reservoir", "Lake/reservoir"),
    ("Artificial", "Artificial"),
)
climate_choices = (
    ("Temperate", "Temperate"),
    ("Tropical/subtropical", "Tropical/subtropical"),
    ("Dry", "Dry"),
    ("Arctic/subarctic", "Arctic/subarctic"),
    ("Alpine", "Alpine"),
    ("Not specified", "Not specified"),
    ("Other", "Other"),
)
cause_term_choices = (("TBD", "TBD"), ("Water quality", "Water quality"))
cause_measure_choices = (("TBD", "TBD"), ("Nutrients", "Nutrients"))
cause_bio_org_choices = (
    ("Ecosystem", "Ecosystem"),
    ("Community", "Community"),
    ("Population", "Population"),
    ("Individual organism", "Individual organism"),
    ("Sub-organismal", "Sub-organismal"),
)
cause_trajectory_choices = (
    ("Increase", "Increase"),
    ("Decrease", "Decrease"),
    ("Change", "Change"),
    ("Other", "Other"),
)
effect_term_choices = (("TBD", "TBD"), ("Algae", "Algae"))
effect_measure_choices = (("TBD", "TBD"), ("Abundance", "Abundance"))
effect_bio_org_choices = (
    ("Ecosystem", "Ecosystem"),
    ("Community", "Community"),
    ("Population", "Population"),
    ("Individual organism", "Individual organism"),
    ("Sub-organismal", "Sub-organismal"),
)
effect_trajectory_choices = (
    ("Increase", "Increase"),
    ("Decrease", "Decrease"),
    ("Change", "Change"),
    ("No change", "No change"),
    ("Other", "Other"),
)
modifying_factors_choices = (("TBD", "TBD"),)
response_measure_type_choices = (
    ("Correlation coefficient", "Correlation coefficient"),
    ("R-squared", "R-squared"),
    ("Mean difference", "Mean difference"),
    ("ANOVA/PERMANOVA", "ANOVA/PERMANOVA"),
    ("Ratio", "Ratio"),
    ("Slope coefficient (beta)", "Slope coefficient (beta)"),
    ("Ordination", "Ordination"),
    ("Threshold", "Threshold"),
)
response_measure_type_correlation_choices = (
    ("Pearson", "Pearson"),
    ("Spearman", "Spearman"),
    ("Not specified", "Not specified"),
)
response_measure_type_rsq_choices = (
    ("Simple linear", "Simple linear"),
    ("Partial", "Partial"),
    ("Multiple", "Multiple"),
    ("Quantile", "Quantile"),
    ("Not specified", "Not specified"),
)
response_measure_type_ratio_choices = (
    ("Response ratio", "Response ratio"),
    ("Odds ratio", "Odds ratio"),
    ("Risk ratio", "Risk ratio"),
    ("Hazard ratio", "Hazard ratio"),
    ("Not specified", "Not specified"),
)
response_measure_type_meandiff_choices = (
    ("Non-standardized", "Non-standardized"),
    ("Standardized", "Standardized"),
    ("Not specified", "Not specified"),
)
response_measure_type_slope_choices = (
    ("Non-transformed data", "Non-transformed data"),
    ("Transformed data", "Transformed data"),
    ("Not specified", "Not specified"),
)
response_measure_type_ord_choices = (
    ("Canonical correspondence analysis (CCA)", "Canonical correspondence analysis (CCA)"),
    ("Principal components analysis (PCA)", "Principal components analysis (PCA)"),
    ("Multiple discriminant analysis (MDA)", "Multiple discriminant analysis (MDA)"),
    ("Non-multidimensional scaling (NMDS)", "Non-multidimensional scaling (NMDS)"),
    ("Factor analysis", "Factor analysis"),
    ("Not specified", "Not specified"),
)
response_measure_type_thresh_choices = (
    ("Regression tree", "Regression tree"),
    ("Random forest", "Random forest"),
    ("Breakpoint (piecewise) regression", "Breakpoint (piecewise) regression"),
    ("Quantile regression", "Quantile regression"),
    ("Cumulative frequency distribution", "Cumulative frequency distribution"),
    ("Gradient forest analysis", "Gradient forest analysis"),
    ("Non-linear curve fitting", "Non-linear curve fitting"),
    ("Ordination", "Ordination"),
    ("TITAN", "TITAN"),
    ("Not specified", "Not specified"),
)
response_variability_choices = (
    ("95% CI", "95% CI"),
    ("90% CI", "90% CI"),
    ("Standard deviation", "Standard deviation"),
    ("Standard error", "Standard error"),
    ("Not applicable", "Not applicable"),
)
statistical_sig_measure_type_choices = (
    ("P-value", "P-value"),
    ("F statistic", "F statistic"),
    ("Chi square", "Chi square"),
    ("Not applicable", "Not applicable"),
)
sort_choices = (("TBD", "TBD"),)


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
    )  # this field is dependent on selecting terrestrial habitat

    habitat_aquatic_freshwater = models.CharField(
        verbose_name="Freshwater habitat",
        max_length=100,
        choices=habitat_aquatic_freshwater_choices,
        blank=True,
        help_text="If you selected freshwater, pick the type of freshwater habitat",
    )  # this field is dependent on selecting aquatic habitat

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

    species = models.CharField(
        verbose_name="Cause species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
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

    species = models.CharField(
        verbose_name="Effect species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
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

    class Meta:
        verbose_name = "Quantitative response information"
