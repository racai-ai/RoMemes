import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from imblearn.over_sampling import SMOTE  # Import SMOTE
import sys
from drop_functions import drop_numbers, drop_columns

def forest_with_smote():
    df = pd.read_csv("en_feature_df.csv")
    drop_numbers(df)

    df.drop(['Text', 'Unnamed: 0', 'Original_text', 'lex_prediction1', 'lex_prediction2', 'bert_s1', 'bert_s2', 'Complexity', 'Real_Fake', 'bert_s1_Negative', 'bert_s2_Surprise', 'Real_Fake_DeepFake',], axis=1, inplace=True)
    df = df.astype(float)
    X = df.iloc[:, :-2]
    y1 = df.iloc[:, -2]
    y2 = df.iloc[:, -1]

    X_train, X_temp, y1_train, y1_temp, y2_train, y2_temp = train_test_split(X, y1, y2, test_size=0.3, random_state=42)
    X_dev, X_test, y1_dev, y1_test, y2_dev, y2_test = train_test_split(X_temp, y1_temp, y2_temp, test_size=0.5,
                                                                       random_state=42)

    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 4],
        'min_samples_leaf': [1, 2]
    }

    def random_forest(sentiment, X_train, X_dev, X_test, y_train, y_dev, y_test, drop_list):
        X_train = drop_columns(X_train, drop_list)
        X_dev = drop_columns(X_dev, drop_list)
        X_test = drop_columns(X_test, drop_list)

        # Apply SMOTE to the training data
        smote = SMOTE(random_state=42)
        X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

        rf = RandomForestClassifier(random_state=42)
        skf = StratifiedKFold(n_splits=5)
        grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=skf, scoring='f1_weighted')
        grid_search.fit(X_train_sm, y_train_sm)
        print(f"Best hyperparameters for {sentiment}:", grid_search.best_params_)
        best_rf = grid_search.best_estimator_

        # Extract and print feature importance
        feature_importance = best_rf.feature_importances_
        feature_names = X_train.columns  # Assuming X_train is a DataFrame with column names
        importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': feature_importance})
        importance_df.sort_values(by='Importance', ascending=False, inplace=True)

        print(f"Feature Importance for {sentiment}:")
        print(importance_df)

        def evaluate(model, X, y):
            y_pred = model.predict(X)
            accuracy = accuracy_score(y, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average='weighted', zero_division=0)
            return {'accuracy': round(accuracy, 3), 'precision': round(precision, 3), 'recall': round(recall, 3),
                    'f1': round(f1, 3)}

        dev_metrics = evaluate(best_rf, X_dev, y_dev)
        print(f'Dev Metrics for {sentiment}:', dev_metrics)

        y_dev_pred = best_rf.predict(X_dev)
        labels = sorted(y_train.unique())
        cm_dev = confusion_matrix(y_dev, y_dev_pred, labels=labels)
        print(f'Confusion Matrix for {sentiment} on Dev Set:')
        print(cm_dev)

        test_metrics = evaluate(best_rf, X_test, y_test)
        print(f'Test Metrics for {sentiment}:', test_metrics)

        y_test_pred = best_rf.predict(X_test)
        cm_test = confusion_matrix(y_test, y_test_pred, labels=labels)
        print(f'Confusion Matrix for {sentiment} on Test Set:')
        print(cm_test)

    with open('../random_forest_output.txt', 'w') as f:
        sys.stdout = f
        random_forest('Sentiment1', X_train, X_dev, X_test, y1_train, y1_dev, y1_test, ['lex_prediction2', 'confidence2',   'bert' ])
        print()
        random_forest('Sentiment2', X_train, X_dev, X_test, y2_train, y2_dev, y2_test, ['lex_prediction1', 'confidence1', 'len_values', 'bert' ])
        sys.stdout = sys.__stdout__

forest_with_smote()
