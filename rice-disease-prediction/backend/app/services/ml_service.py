"""
ML Service — Model loading, inference, and disease information lookup.

Supports a demo mode when no trained model weights are available,
allowing full app testing without a GPU-trained model.
"""

import os
import random
import logging
from typing import Dict, List, Tuple, Optional

import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Disease Classes ───
DISEASE_CLASSES = {
    0: {
        "name": "Healthy",
        "description": "The rice leaf shows no signs of disease. The plant appears to be in good health with normal green coloration and structure.",
        "symptoms": ["Uniform green color", "No lesions or spots", "Normal leaf structure", "No discoloration"],
        "treatment": {
            "chemical": "No treatment needed. Continue regular fertilization schedule.",
            "organic": "Maintain healthy soil with compost and proper crop rotation.",
            "prevention": "Regular monitoring, balanced nutrition, proper water management."
        },
        "severity": "none"
    },
    1: {
        "name": "Blast",
        "description": "Rice blast caused by Magnaporthe oryzae is one of the most destructive diseases of rice. It can infect all above-ground parts of the plant at any growth stage.",
        "symptoms": [
            "Diamond-shaped lesions with gray centers",
            "Brown borders on leaves",
            "Lesions may coalesce killing entire leaves",
            "Node blast causes stem breakage",
            "Panicle neck blast causes white, unfilled grains"
        ],
        "treatment": {
            "chemical": "Apply Tricyclazole 75% WP (0.6g/L) or Isoprothiolane 40% EC (1.5mL/L). Spray at tillering and booting stages.",
            "organic": "Use Trichoderma-based biocontrol agents. Apply neem oil spray (5mL/L). Silicon amendments improve resistance.",
            "prevention": "Use resistant varieties (e.g., CO-39, IR-64). Avoid excessive nitrogen. Maintain proper plant spacing. Remove infected crop debris."
        },
        "severity": "high"
    },
    2: {
        "name": "Brown Spot",
        "description": "Brown spot disease caused by Bipolaris oryzae (Cochliobolus miyabeanus). It is associated with nutrient-deficient soils and affects grain quality.",
        "symptoms": [
            "Oval brown lesions on leaves",
            "Lesions have dark brown margins and gray centers",
            "Small dark spots on hulls and grains",
            "Seedling blight in severe cases",
            "Leaves may dry out and die"
        ],
        "treatment": {
            "chemical": "Spray Mancozeb 75% WP (2.5g/L) or Propiconazole 25% EC (1mL/L) at disease onset. Repeat after 15 days if needed.",
            "organic": "Seed treatment with Pseudomonas fluorescens (10g/kg seed). Apply potassium-rich organic fertilizers to strengthen plants.",
            "prevention": "Use certified disease-free seeds. Maintain soil fertility with balanced NPK. Avoid water stress. Apply potash fertilizers."
        },
        "severity": "medium"
    },
    3: {
        "name": "Sheath Blight",
        "description": "Sheath blight caused by Rhizoctonia solani is a major fungal disease that causes significant yield losses worldwide, especially in warm, humid conditions.",
        "symptoms": [
            "Oval or irregular greenish-gray lesions on leaf sheaths",
            "Lesions with dark brown borders",
            "Banding pattern as lesions merge",
            "Infected sheaths turn brown and dry",
            "Lodging in severe cases"
        ],
        "treatment": {
            "chemical": "Apply Validamycin 3% SL (2.5mL/L) or Hexaconazole 5% EC (2mL/L). Spray at maximum tillering and panicle initiation.",
            "organic": "Apply Trichoderma viride (5g/L) as foliar spray. Use biocontrol agent Bacillus subtilis. Incorporate green manure.",
            "prevention": "Avoid dense planting. Reduce nitrogen dosage. Maintain proper water drainage. Clean field of debris. Burn stubble after harvest."
        },
        "severity": "high"
    },
    4: {
        "name": "Bacterial Leaf Blight",
        "description": "Bacterial leaf blight (BLB) caused by Xanthomonas oryzae pv. oryzae is one of the most serious bacterial diseases of rice, prevalent in both tropical and temperate regions.",
        "symptoms": [
            "Water-soaked lesions on leaf margins",
            "Lesions turn yellow to white as they enlarge",
            "Leaves dry from tip backward",
            "Milky or yellowish bacterial ooze on leaf surface",
            "Wilting of seedlings (kresek phase)"
        ],
        "treatment": {
            "chemical": "Spray Streptomycin sulfate + Tetracycline (300ppm) or Copper oxychloride 50% WP (3g/L). Avoid overhead irrigation.",
            "organic": "Apply neem cake to soil (150kg/ha). Foliar spray of Pseudomonas fluorescens (10g/L). Zinc sulfate application helps.",
            "prevention": "Use BLB-resistant varieties. Avoid clipping seedling tips during transplanting. Balanced nitrogen use. Proper drainage."
        },
        "severity": "high"
    },
    5: {
        "name": "Tungro",
        "description": "Rice tungro disease is caused by the combination of Rice tungro bacilliform virus (RTBV) and Rice tungro spherical virus (RTSV), transmitted by green leafhoppers.",
        "symptoms": [
            "Yellow to orange-yellow discoloration of leaves",
            "Stunted plant growth",
            "Reduced tillering",
            "Delayed flowering",
            "Partially filled or empty grains"
        ],
        "treatment": {
            "chemical": "No direct chemical cure for viral diseases. Control vector (green leafhoppers) with Imidacloprid 17.8% SL (0.5mL/L) or Thiamethoxam 25% WG (0.2g/L).",
            "organic": "Use light traps to monitor and control leafhoppers. Apply neem seed kernel extract (5%). Encourage natural predators like spiders and dragonflies.",
            "prevention": "Use tungro-resistant varieties. Synchronous planting in the community. Remove infected plants (roguing). Avoid staggered planting."
        },
        "severity": "high"
    },
    6: {
        "name": "False Smut",
        "description": "False smut caused by Ustilaginoidea virens affects rice panicles, replacing individual grains with large velvety green spore balls that turn orange and black.",
        "symptoms": [
            "Large velvety green spore balls on individual grains",
            "Spore balls turn yellowish-orange then greenish-black",
            "Usually only a few grains per panicle affected",
            "Chalkiness in surrounding grains",
            "Reduced grain weight and quality"
        ],
        "treatment": {
            "chemical": "Spray Propiconazole 25% EC (1mL/L) or Copper hydroxide 77% WP (2.5g/L) at booting stage. Preventive application is crucial.",
            "organic": "Apply Trichoderma harzianum (5g/L) at booting. Use biocontrol formulations. Remove and destroy infected panicles.",
            "prevention": "Use resistant varieties. Avoid excessive nitrogen. Proper spacing for air circulation. Seed treatment before sowing."
        },
        "severity": "medium"
    },
    7: {
        "name": "Narrow Brown Leaf Spot",
        "description": "Narrow brown leaf spot caused by Cercospora janseana (Sphaerulina oryzina). It produces narrow, linear brown lesions on leaves and leaf sheaths.",
        "symptoms": [
            "Narrow, linear brown lesions parallel to leaf veins",
            "Lesions are short and dark brown",
            "May coalesce causing large brown areas",
            "Leaves turn brown in severe infections",
            "Reduced photosynthetic area"
        ],
        "treatment": {
            "chemical": "Apply Mancozeb 75% WP (2.5g/L) or Carbendazim 50% WP (1g/L). Spray at first symptom appearance.",
            "organic": "Foliar application of compost tea. Potassium silicate spray strengthens cell walls. Apply Pseudomonas fluorescens.",
            "prevention": "Balanced fertilization with adequate potassium. Avoid water stress. Use resistant varieties. Proper crop rotation."
        },
        "severity": "low"
    },
}

NUM_CLASSES = len(DISEASE_CLASSES)


class MLService:
    """
    Singleton ML service for rice disease prediction.
    Falls back to demo mode if no trained model is available.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.demo_mode = False
        self.transform = self._build_transform()
        self._load_model()

    def _build_transform(self) -> transforms.Compose:
        """Build the preprocessing transform pipeline (matches training)."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def _build_model(self) -> nn.Module:
        """Build EfficientNet-B3 with custom classifier head."""
        model = models.efficientnet_b3(weights=None)
        # Replace classifier: 1536 → 512 → num_classes
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(1536, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(512, NUM_CLASSES),
        )
        return model

    def _load_model(self):
        """Load model weights from checkpoint file."""
        model_path = settings.MODEL_PATH

        if not os.path.exists(model_path):
            logger.warning(
                f"Model file not found at {model_path}. "
                "Running in DEMO MODE with simulated predictions."
            )
            self.demo_mode = True
            # Still build the model architecture (needed for Grad-CAM structure)
            self.model = self._build_model()
            self.model.to(self.device)
            self.model.eval()
            return

        try:
            self.model = self._build_model()
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)

            # Support both raw state_dict and checkpoint dict
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                self.model.load_state_dict(checkpoint["model_state_dict"])
                logger.info(
                    f"Loaded model checkpoint — "
                    f"Epoch: {checkpoint.get('epoch', '?')}, "
                    f"Val Acc: {checkpoint.get('val_accuracy', '?')}"
                )
            else:
                self.model.load_state_dict(checkpoint)
                logger.info("Loaded model state dict successfully.")

            self.model.to(self.device)
            self.model.eval()
            self.demo_mode = False
            logger.info(f"ML model ready on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}. Falling back to demo mode.")
            self.demo_mode = True
            self.model = self._build_model()
            self.model.to(self.device)
            self.model.eval()

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess a PIL Image for model inference.
        Returns a batch tensor of shape (1, 3, 224, 224).
        """
        if image.mode != "RGB":
            image = image.convert("RGB")
        tensor = self.transform(image)
        return tensor.unsqueeze(0)  # Add batch dimension

    def predict(self, image: Image.Image) -> Tuple[int, float, List[Dict]]:
        """
        Run inference on a PIL Image.

        Returns:
            (predicted_class_idx, confidence, all_probabilities)
            where all_probabilities is a list of {"class_name": str, "probability": float}
        """
        if self.demo_mode:
            return self._demo_predict()

        input_tensor = self.preprocess_image(image).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]

        probs_np = probabilities.cpu().numpy()
        predicted_class = int(np.argmax(probs_np))
        confidence = float(probs_np[predicted_class])

        all_probs = [
            {
                "class_name": DISEASE_CLASSES[i]["name"],
                "probability": round(float(probs_np[i]), 4),
            }
            for i in range(NUM_CLASSES)
        ]
        # Sort by probability descending
        all_probs.sort(key=lambda x: x["probability"], reverse=True)

        return predicted_class, confidence, all_probs

    def _demo_predict(self) -> Tuple[int, float, List[Dict]]:
        """Generate realistic-looking demo predictions."""
        # Pick a random disease (weighted toward diseases, not healthy)
        weights = [0.05, 0.18, 0.18, 0.15, 0.15, 0.10, 0.10, 0.09]
        predicted_class = random.choices(range(NUM_CLASSES), weights=weights, k=1)[0]

        # Generate realistic probabilities
        probs = np.random.dirichlet(np.ones(NUM_CLASSES) * 0.3)
        # Make the predicted class dominant
        probs[predicted_class] = 0
        remaining = probs / probs.sum() * (1 - random.uniform(0.75, 0.95))
        confidence = 1 - remaining.sum()
        probs[predicted_class] = confidence
        probs = probs.tolist()

        all_probs = [
            {
                "class_name": DISEASE_CLASSES[i]["name"],
                "probability": round(probs[i], 4),
            }
            for i in range(NUM_CLASSES)
        ]
        all_probs.sort(key=lambda x: x["probability"], reverse=True)

        return predicted_class, round(confidence, 4), all_probs

    def get_disease_info(self, class_idx: int) -> Dict:
        """Get full disease information for a class index."""
        return DISEASE_CLASSES.get(class_idx, DISEASE_CLASSES[0])

    def get_input_tensor(self, image: Image.Image) -> torch.Tensor:
        """Get preprocessed tensor (needed by GradCAM service)."""
        return self.preprocess_image(image).to(self.device)


# Singleton instance
ml_service = MLService()
