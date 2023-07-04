# COCO Merge

COCO Format Bounding Box Dataset Integration Process

The data used as an example is the COCO2017 Val 000000000139.jpg, 000000000285.jpg and the modified JSON

```bash
python merge_dataset.py  --base_json coco_custom1/annotations/sample_annotation1.json --base_image_path coco_custom1/images/ --add_json coco_custom2/annotations/sample_annotation2.json --add_image_path coco_custom2/images/ --unified_json_path coco_merge/annotations/merge_annotation.json --unified_image_path coco_merge/images/ 
```

