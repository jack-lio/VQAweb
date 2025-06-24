
import torch
import numpy as np
from PIL import Image
from torchvision import models, transforms
from m_model import CNN, TabularMLP
from torchvision import models, transforms
class FeatureManager():
    def __init__(self, args: dict):
        self.args = args
        if 'feature_type' in args:
            self.initialize_feature_module()

    def initialize_feature_module(self):
        self.device = torch.device("cpu")
        if torch.cuda.is_available():
            print("GPU available, use GPU")

        if self.args['feature_type'] == 'mobilenet_v2':
            self.model = models.mobilenet_v2(pretrained=True)
            self.model.classifier = self.model.classifier[:-1]
            self.model = self.model.to(self.device)
            self.model.eval()

            self.img_transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
            ])

        elif self.args['feature_type'] == 'custom_cnn':
            self.model = CNN().to(self.device)
            self.model.eval()

            self.img_transform = transforms.Compose([
                transforms.Resize((128, 128)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                     std=[0.5, 0.5, 0.5])
            ])

        elif self.args['feature_type'] == 'tabular_mlp':
            input_size = self.args.get("input_size", 5)
            self.model = TabularMLP(input_size=input_size).to(self.device)
            self.model.eval()

    def extract_img_features(self, img_input) -> np.array:
        if isinstance(img_input, Image.Image):
            input_image = img_input
        else:
            input_image = Image.open(img_input).convert('RGB')

        input_tensor = self.img_transform(input_image)
        with torch.no_grad():
            input_data = input_tensor.to(self.device).unsqueeze(dim=0)
            features = self.model(input_data).detach().cpu().numpy()
        return features

    def extract_tabular_feature(self, input_vector: np.ndarray) -> np.ndarray:
        assert self.model is not None, "Model has not been initialized!"
        input_tensor = torch.tensor(input_vector, dtype=torch.float32).to(self.device).unsqueeze(0)
        with torch.no_grad():
            features = self.model(input_tensor).detach().cpu().numpy()
        return features.squeeze(0)
