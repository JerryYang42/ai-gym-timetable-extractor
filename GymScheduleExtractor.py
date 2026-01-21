from OcrEngine import OcrEngine, GeminiOcrEngine

class GymScheduleExtractor:
    def __init__(self, ocr_engine: OcrEngine):
        self.ocr_engine = ocr_engine

    def extract(self, image_path):
        return self.ocr_engine.extract_image_as_json(image_path)

    def save_to_file(self, content, output_path):
        """Saves content to a file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved extracted JSON to {output_path}")


if __name__ == "__main__":
    gemini_ocr_engine = GeminiOcrEngine()
    extractor = GymScheduleExtractor(ocr_engine=gemini_ocr_engine)
    filenames = ["IMG_7191"]
    for name in filenames:
        input_path = f"data/{name}.PNG"
        output_path = f"output2/{name}.json"
        json_result = extractor.extract(input_path)
        extractor.save_to_file(json_result, output_path)
    

    # json_result = extractor.extract("data/IMG_7194.PNG")
    # print(json_result)
    # extractor.save_to_file(json_result, "output/IMG_7194.json")