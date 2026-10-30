"""Train reproducible baseline classifiers and export evaluation evidence."""
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, roc_auc_score, RocCurveDisplay
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/"outputs"; FIG=ROOT/"figures"; OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
df=pd.read_csv(ROOT/"spacex_cleaned_data.csv")
features=[c for c in ["FlightNumber","PayloadMass","Flights","GridFins","Reused","Legs","Block","ReusedCount","Orbit","LaunchSite","Serial"] if c in df]
X=df[features]; y=df["Class"].astype(int)
num=X.select_dtypes(include=[np.number,"bool"]).columns.tolist(); cat=[c for c in features if c not in num]
prep=ColumnTransformer([("num",Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())]),num),("cat",Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),cat)])
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
models={"Logistic Regression":LogisticRegression(max_iter=2000,class_weight="balanced",random_state=42),"Decision Tree":DecisionTreeClassifier(max_depth=5,class_weight="balanced",random_state=42)}
rows=[]; reports=[]; fig,ax=plt.subplots(figsize=(7,6))
for name,est in models.items():
 pipe=Pipeline([("preprocess",prep),("model",est)]); pipe.fit(Xtr,ytr); pred=pipe.predict(Xte); prob=pipe.predict_proba(Xte)[:,1]
 cm=confusion_matrix(yte,pred,labels=[0,1]); pd.DataFrame(cm,index=["actual_0","actual_1"],columns=["predicted_0","predicted_1"]).to_csv(FIG/f"confusion_{name.lower().replace(' ','_')}.csv")
 fig_cm,ax_cm=plt.subplots(figsize=(5,4)); ax_cm.imshow(cm,cmap="Blues"); ax_cm.set(xticks=[0,1],yticks=[0,1],xticklabels=["0","1"],yticklabels=["0","1"],xlabel="Predicted",ylabel="Actual",title=f"{name} confusion matrix");
 for (i,j),v in np.ndenumerate(cm): ax_cm.text(j,i,str(v),ha="center",va="center")
 fig_cm.tight_layout(); fig_cm.savefig(FIG/f"confusion_{name.lower().replace(' ','_')}.png",dpi=160); plt.close(fig_cm)
 rep=classification_report(yte,pred,labels=[0,1],target_names=["Unsuccessful","Successful"],output_dict=True,zero_division=0)
 for label,vals in rep.items():
  if isinstance(vals,dict): reports.append({"Model":name,"Class":label,**vals})
 auc=roc_auc_score(yte,prob); RocCurveDisplay.from_predictions(yte,prob,name=f"{name} (AUC={auc:.3f})",ax=ax)
 rows.append({"Model":name,"Accuracy":accuracy_score(yte,pred),"Precision":precision_score(yte,pred,zero_division=0),"Recall":recall_score(yte,pred,zero_division=0),"F1 score":f1_score(yte,pred,zero_division=0),"ROC-AUC":auc,"TN":cm[0,0],"FP":cm[0,1],"FN":cm[1,0],"TP":cm[1,1]})
fig.tight_layout(); fig.savefig(FIG/"roc_curves.png",dpi=160); plt.close(fig)
metrics=pd.DataFrame(rows); metrics.to_csv(ROOT/"spacex_model_comparison.csv",index=False); metrics.to_csv(OUT/"model_metrics.csv",index=False); pd.DataFrame(reports).to_csv(OUT/"classification_reports.csv",index=False)
print(metrics.to_string(index=False)); print("Saved reports, confusion matrices and ROC curves.")
