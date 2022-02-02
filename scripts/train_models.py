from enum import Enum
from operator import mod
import pickle
import typer
from pathlib import Path
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier


class ModelType(str, Enum):
    lr = "LogisticRegression"
    dt = "DecisionTree"


def train_model(model_type: ModelType):
    # load toy dataset
    data = load_iris()

    model_dir = Path(__file__).parent.parent / "models"

    if model_type == ModelType.dt:
        model = DecisionTreeClassifier(random_state=0)
        model_path = model_dir / "dt.model"
    elif model_type == ModelType.lr:
        model = LogisticRegression(random_state=0)
        model_path = model_dir / "lr.model"
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # train model
    model.fit(data.data, data.target)

    # dump model
    model_path.parent.mkdir(exist_ok=True, parents=True)
    pickle.dump(model, model_path.open("wb"))

    typer.echo(f"model dumped to {str(model_path.absolute())}")


if __name__ == "__main__":
    typer.run(train_model)
