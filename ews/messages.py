class Message:
    CHANGE_POST_NOT_ALLOWED = "You are not allowed to change this post."
    ERROR_AREAS_WITHOUT_PREDICTORS_OR_DATA = ("Error: Areas do not"
                                              "include any"
                                              "predictor variables, "
                                              "or existing predictor "
                                              "variables do not contain "
                                              "any data.")
    ERROR_NO_COMMON_DATES = ("Error: no common dates in feature data"
                             "and 'areavars'.")
    ERROR_NO_DATA_FOR_SUMMER_MONTHS = ("Error: No data available for "
                                       "summer months "
                                       "(May to September).")
    ERROR_NO_FEATURE_TYPE_NAMED = 'No feature type named "{}" found.'
    ERROR_QUERYING_BATHING_SPOTS = ("Querying the database for "
                                    "bathing spots raised an error. "
                                    "Most likely the category BathingSpot "
                                    "has not been created so far.")
    FEATURE_IMPORTANCE_OF_RF_MODEL = ("Feature importance of "
                                      "Random Forest model")
    FORM_NOT_VALID = "Form not valid."
    IT_WORKED = "It worked."
    MODEL_NOT_FOUND = "Model not found."
    NO_BATHING_SPOTS = ("There are currently no bathing spots. "
                        "Create some and start modelling.")
    PAGE_NOT_FOUND = "404: Page ot found."
    PASSWORDS_MUST_MATCH = "Passwords must match."
    POST_REQUEST_REQUIRED = "POST request required."
    SUBMISSION_FAILED = "Submission not successful."
    USERNAME_ALREADY_TAKEN = "Username already taken."
