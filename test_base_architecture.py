#!/usr/bin/env python3
"""
Test the base model architecture
"""

from src.models.base import BaseModel, PipelineComponent
from src.utils.logging import logger

class TestModel(BaseModel):
    """Test implementation of BaseModel"""
    
    def load_model(self):
        self.logger.info(f"Loading test model: {self.model_name}")
        # Simulate model loading
        self.model = "pretend_model"
        self.processor = "pretend_processor"
    
    def process(self, input_data):
        self.logger.info(f"Processing: {input_data}")
        return f"Processed: {input_data}"

class TestComponent(PipelineComponent):
    """Test implementation of PipelineComponent"""
    
    def process(self, data):
        return data.upper()

def test_base_architecture():
    print("Testing Base Model Architecture...")
    
    # Test BaseModel
    with TestModel("test-model") as model:
        result = model.process("test input")
        print(f"✓ BaseModel result: {result}")
    
    # Test PipelineComponent with error handling
    component = TestComponent("test-component")
    result = component.safe_process("hello world")
    print(f"✓ PipelineComponent result: {result}")
    
    print("✓ Base architecture working correctly!")

if __name__ == "__main__":
    test_base_architecture()
