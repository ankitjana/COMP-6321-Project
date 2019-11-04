import pandas as pd
from scipy.io import arff
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, KFold, GridSearchCV

dataset = pd.read_csv(r'data/Steel_plates_faults/Faults.NNA', header=None, delimiter='	',
                      names=['X_Minimum', 'X_Maximum', 'Y_Minimum', 'Y_Maximum', 'Pixels_Areas', 'X_Perimeter',
                             'Y_Perimeter',
                             'Sum_of_Luminosity', 'Minimum_of_Luminosity', 'Maximum_of_Luminosity',
                             'Length_of_Conveyer',
                             'TypeOfSteel_A300', 'TypeOfSteel_A400', 'Steel_Plate_Thickness', 'Edges_Index',
                             'Empty_Index',
                             'Square_Index', 'Outside_X_Index', 'Edges_X_Index', 'Edges_Y_Index',
                             'Outside_Global_Index', 'LogOfAreas',
                             'Log_X_Index', 'Log_Y_Index', 'Orientation_Index', 'Luminosity_Index', 'SigmoidOfAreas',
                             'Pastry',
                             'Z_Scratch', 'K_Scatch', 'Stains', 'Dirtiness', 'Bumps', 'Other_Faults'])

# y = dataset[['Pastry', 'Z_Scratch', 'K_Scatch', 'Stains', 'Dirtiness', 'Bumps', 'Other_Faults']]
y = dataset.loc[:, 'Pastry':'Other_Faults']
dataset.drop(['Pastry', 'Z_Scratch', 'K_Scatch', 'Stains', 'Dirtiness', 'Bumps', 'Other_Faults'], axis=1, inplace=True)

cat_si_step = ('si', SimpleImputer(strategy='constant', fill_value=-99))  # This is for training
ohe_step = ('ohe', OneHotEncoder(sparse=False, handle_unknown='ignore'))  # This is for testing
oe_step = ('le', OrdinalEncoder())
num_si_step = ('si', SimpleImputer(strategy='median'))
sc_step = ('sc', StandardScaler())

cat_pipe = Pipeline([cat_si_step, ohe_step])
num_pipe = Pipeline([num_si_step, sc_step])
bin_pipe = Pipeline([oe_step])

transformers = [
    ('cat', cat_pipe, ['Outside_Global_Index']),
    ('num', num_pipe, ['X_Minimum', 'X_Maximum', 'Y_Minimum', 'Y_Maximum', 'Pixels_Areas', 'X_Perimeter', 'Y_Perimeter',
                       'Sum_of_Luminosity', 'Minimum_of_Luminosity', 'Maximum_of_Luminosity', 'Length_of_Conveyer',
                       'Steel_Plate_Thickness', 'Edges_Index', 'Empty_Index', 'Square_Index', 'Outside_X_Index',
                       'Edges_X_Index', 'Edges_Y_Index', 'LogOfAreas', 'Log_X_Index', 'Log_Y_Index',
                       'Orientation_Index', 'Luminosity_Index', 'SigmoidOfAreas']),
    ('bin', bin_pipe, ['TypeOfSteel_A300', 'TypeOfSteel_A400']),
]

ct = ColumnTransformer(transformers=transformers)
# X_transformed = ct.fit_transform(dataset)

lr_pipe = Pipeline([
    ('X_transform', ct),
    ('lr', LogisticRegression(penalty='l1', solver='liblinear', max_iter=800)),
])

kf = KFold(n_splits=5, shuffle=True)
# cv_score = cross_val_score(ml_pipe, dataset, y, cv=kf).mean()

param_grid = {
    'X_transform__num__si__strategy': ['mean', 'median'],
    'lr__penalty': ['l2'],
    'lr__solver': ['saga', 'lbfgs', 'liblinear', 'sag', 'newton-cg'],
}
# lr_pipe.fit(dataset, y)
nb_pipe = Pipeline([
    ('X_transform', ct),
    ('lr', GaussianNB(priors=None, var_smoothing=1e-01)),
])

nb_param_grid = {
    'X_transform__num__si__strategy': ['mean', 'median'],

}
print(
    "########################################## LOGISTIC REGRESSION ON STEEL_PLATES DATA ########################################## ")
grid_search_lr = GridSearchCV(lr_pipe, param_grid, cv=kf)
grid_search_lr.fit(dataset, y)
print(grid_search_lr.best_params_)
print('The CV best score:', grid_search_lr.best_score_)
print(f'The train set score: {grid_search_lr.score(dataset, y)} ')
print()
print(
    "########################################## NAIVE BAYES STEEL_PLATES DATA ########################################## ")
grid_search_nb = GridSearchCV(nb_pipe, nb_param_grid, cv=kf)
grid_search_nb.fit(dataset, y)
print(grid_search_nb.best_params_)
print('The CV best score:', grid_search_nb.best_score_)
print(f'The train set score: {grid_search_nb.score(dataset, y)} ')
