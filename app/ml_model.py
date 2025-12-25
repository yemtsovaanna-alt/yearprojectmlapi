import io
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
from typing import Optional
import json


class ImageClassificationModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        self.model.eval()
        self.model.to(self.device)

        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        with open(self._get_imagenet_classes_path(), 'r') as f:
            self.classes = json.load(f)

    def _get_imagenet_classes_path(self) -> str:
        return "app/imagenet_classes.json"

    def predict_from_bytes(self, image_bytes: bytes, top_k: int = 5) -> Optional[dict]:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

            top_probs, top_indices = torch.topk(probabilities, top_k)

            predictions = []
            for prob, idx in zip(top_probs.cpu().numpy(), top_indices.cpu().numpy()):
                predictions.append({
                    "class": self.classes.get(str(idx), f"class_{idx}"),
                    "probability": float(prob)
                })

            return {
                "predictions": predictions,
                "top_class": predictions[0]["class"],
                "top_probability": predictions[0]["probability"]
            }
        except Exception as e:
            return None


ml_model = ImageClassificationModel()
