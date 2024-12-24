const seErrorWarning =
        "Standard errors estimates are not generated for parameters estimated on corresponding bounds, although sampling error is present for all parameters, as a rule. Standard error estimates may not be reliable as a basis for confidence intervals or tests when one or more parameters are on bounds.",
    testFootnotes = {
        1: "Test the null hypothesis that responses and variances do not differ among dose levels (A2 vs R). If this test fails to reject the null hypothesis (p-value > 0.05), there may not be a dose-response.",
        2: "Test the null hypothesis that variances are homogenous (A1 vs A2). If this test fails to reject the null hypothesis (p-value > 0.05), the simpler constant variance model may be appropriate.",
        3: "Test the null hypothesis that the variances are adequately modeled (A3 vs A2). If this test fails to reject the null hypothesis (p-value > 0.05), it may be inferred that the variances have been modeled appropriately.",
        4: "Test the null hypothesis that the model for the mean fits the data (Fitted vs A3). If this test fails to reject the null hypothesis (p-value > 0.1), the user has support for use of the selected model.",
    };

export {seErrorWarning, testFootnotes};
