import uuid
import json
from typing import Dict, List, Any, Optional, Union

class HexacinInferenceEngine:
    def __init__(self) -> None:
        self.engine_version: str = "3.0.0-PROD"
        
        
        self.homeostatic_baselines: Dict[str, Dict[str, float]] = {
            "body_temperature": {"max": 37.5, "min": 35.5},
            "heart_rate": {"max": 100.0, "min": 60.0},
            "systolic_blood_pressure": {"max": 130.0, "min": 90.0},
            "c_reactive_protein": {"max": 5.0, "min": 0.0},
            "arterial_ph": {"max": 7.45, "min": 7.35},
            "white_blood_cell_count": {"max": 11000.0, "min": 4000.0}
        }
        
        
        self.nosological_matrix: Dict[str, Dict[str, Any]] = {
            "sepsis": {
                "clinical_indicators": {
                    "c_reactive_protein": lambda v: v > 100, 
                    "white_blood_cell_count": lambda v: v > 12000, 
                    "body_temperature": lambda v: v > 38.5
                },
                "metadata": {
                    "disease_name": "Severe Sepsis / Septic Shock Risk", 
                    "icd_10_code": "A41.9", 
                    "urgency_level": "CRITICAL"
                }
            },
            "ketoacidosis": {
                "clinical_indicators": {
                    "arterial_ph": lambda v: v < 7.3, 
                    "white_blood_cell_count": lambda v: v > 15000
                },
                "metadata": {
                    "disease_name": "Diabetic Ketoacidosis (DKA)", 
                    "icd_10_code": "E11.11", 
                    "urgency_level": "CRITICAL"
                }
            }
        }

    def ingest_and_diagnose(self, patient_payload: Union[str, Dict[str, Any]]) -> str:
        """
        
        """
        try:
            if isinstance(patient_payload, str):
                profile = json.loads(patient_payload)
            else:
                profile = patient_payload
        except Exception:
            return json.dumps({"status": "IO_ERROR", "message": "Invalid payload format. Expected JSON string or Dict."}, ensure_ascii=False)

        vitals: Dict[str, float] = profile.get("vitals", {})
        biomarkers: Dict[str, float] = profile.get("biomarkers", {})
        unified_metrics = {**vitals, **biomarkers}
        
        target_pathology: Optional[Dict[str, Any]] = None
        highest_indicator_match: int = 0

        
        for pathology_id, criteria in self.nosological_matrix.items():
            matched_indicators = 0
            for metric, conditional_validator in criteria["clinical_indicators"].items():
                if metric in unified_metrics and conditional_validator(unified_metrics[metric]):
                    matched_indicators += 1
            
            if matched_indicators > highest_indicator_match and matched_indicators >= len(criteria["clinical_indicators"]) - 1:
                highest_indicator_match = matched_indicators
                target_pathology = criteria["metadata"]

        if target_pathology:
            return json.dumps({
                "status": "DIAGNOSTIC_MATCH_FOUND",
                "execution_profile": "DETERMINISTIC_EXPERT_SYSTEM",
                "payload": target_pathology
            }, indent=2, ensure_ascii=False)

        
        systemic_anomalies: List[str] = []
        for metric, baseline in self.homeostatic_baselines.items():
            if metric in unified_metrics:
                current_value = unified_metrics[metric]
                if current_value > baseline["max"]:
                    systemic_anomalies.append(f"Hyper-{metric} (Value: {current_value})")
                elif current_value < baseline["min"]:
                    systemic_anomalies.append(f"Hypo-{metric} (Value: {current_value})")

        if len(systemic_anomalies) >= 2:
            novel_pathology_id = f"HEXACIN-MUT-{uuid.uuid4().hex[:6].upper()}"
            return json.dumps({
                "status": "NOVEL_PATHOLOGY_SYNTHESIZED",
                "execution_profile": "BIOLOGIC_ANOMALY_ENGINE",
                "payload": {
                    "disease_name": f"Idiopathic Systemic Syndrome ({novel_pathology_id})",
                    "icd_10_code": "U99.9 (Emergency Classification)",
                    "urgency_level": "IMMEDIATE_ISOLATION",
                    "pathophysiological_analysis": f"Critical disruption of fundamental human homeostasis verified: {', '.join(systemic_anomalies)}.",
                    "clinical_directives": [
                        "Initiate non-specific metabolic stabilization.",
                        "Enforce immediate biocontainment/isolation procedures.",
                        "Deploy continuous multi-system biometric telemetry."
                    ]
                }
            }, indent=2, ensure_ascii=False)

        return json.dumps({
            "status": "METRICS_STABLE",
            "payload": {"message": "Patient metrics sit within acceptable physiological limits."}
        }, indent=2, ensure_ascii=False)
