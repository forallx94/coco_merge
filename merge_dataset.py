
import os
import json
import copy
import shutil
from glob import glob
from pathlib import Path
import argparse

class MergeAnnotation():
    def __init__(self, args):
        '''
        COCO Format Bounding Box Dataset Integration Process

            Def :
                load_json : Load the json file
                image_path_check : Check the image inside the json - does the json match the image path?
                category_merge : Check and integrate categories between existing JSON and additional JSON
                image_merge: Put all images in new json
                annotation_merge : Add annotation categories to the new json by modifying them
                save_json : Save new json
                image_move: Move new images to existing image folder
        '''
        self.args = args
        self.base_json = self.load_json(Path(self.args.base_json))
        self.add_json = self.load_json(Path(self.args.add_json))
        self.unified_json = copy.deepcopy(self.base_json)


    def load_json(self, json_path):
        '''
        Load the json file   
        Args:
            json_path : json path
        '''
        with open(json_path,'r') as json_file:
            anno_json = json.load(json_file)
        return anno_json


    def image_path_check(self):
        '''
        Check if an image path in json matches an image in image_path
        Check as a subset, allowing images in anno_json to be a subset of image_path
        Args:
            add_json : Input JSON file  
            add_image_path : Input image folder
        '''
        json_image_set = set([i['file_name'] for i in self.add_json['images']])
        image_set = set([Path(i).name for i in  glob(os.path.join(self.args.add_image_path,'*'))])
        if json_image_set.issubset(image_set):
            return True
        else:
            raise Exception('The image in the image path is different from the image recorded in the annotation file.')
        

    def image_merge(self):
        '''
        Integrating imges inside a JSON file 
        
        Need to know the id of the images
        If it is already set so that it does not conflict with the existing ID, enter it directly
        If it conflicts with the existing ID, modify it and enter it

        Args:
            base_json : JSON file that is already entered.
            add_json : a newly labeled json file to be added.
            unified_json : JSON to be written with old and new labeled together
        '''
        for image_element in self.add_json['images']:
            if image_element not in self.unified_json['images']:
                self.unified_json['images'].append(image_element)


    def category_merge(self):
        '''
        Integrating categories inside a JSON file 

        1. check for base_json subset of add_json (to see what is purely new)
        2. assign IDs to new items
        3. assign new id to unified_json 
        Args:
            base_json : the JSON file that is already labeled.
            add_json : json file to be added with new labeling
            unified_json : JSON to be written with old and new labeled together 
        Return: 
            categpty_id_dict : a dictionary that returns the careogry number from unified_json when the category number from add_json is entered.
        '''
        new_category = set(i['name'] for i in  self.add_json['categories']) - set(i['name'] for i in  self.base_json['categories'])
        new_category_dict ={items['name'] : items['id'] for  items in self.add_json['categories']}
        self.category_id_dict = {}
        start_id_num = int(self.base_json['categories'][-1]['id'])
        for num, category_name in enumerate(new_category):
            self.unified_json['categories'].append({'id' : start_id_num + num + 1 , 'name' : category_name})
            self.category_id_dict[new_category_dict[category_name]] = start_id_num + num + 1


    def annotation_merge(self):
        '''
        The process of integrating annotation items inside a json file 
        
        Integration categories must exist inside unified_json
        id is set after the existing id

        Args:
            add_json : JSON file to be added with new labeling
            unified_json: json file where old and new will be merged and recorded
        '''
        for annotation in self.add_json['annotations']:
            annotation['category_id'] = self.category_id_dict[annotation['category_id']]
            self.unified_json['annotations'].append( annotation )


    def save_json(self):
        '''
        Save the finalized annotation file

        Args:
            unified_json: The finalized JSON file
            unified_json_path: The path to save the finalized json file
        '''
        os.makedirs(Path(self.args.unified_json_path).parent, exist_ok=True)
        with open(self.args.unified_json_path, 'w') as json_file:
            json.dump(self.unified_json, json_file)


    def image_move(self):
        '''
        Copy and paste existing and additional images
        
        Args:
            base_image_path : path to the old image
            add_image_path : New image path
        '''
        os.makedirs(Path(self.args.unified_image_path), exist_ok=True)
        for image_path in glob(self.args.base_image_path +'*'):
            image_path = Path(image_path)
            shutil.copy2(image_path, os.path.join(self.args.unified_image_path,image_path.name))

        for image_path in glob(self.args.add_image_path +'*'):
            image_path = Path(image_path)
            shutil.copy2(image_path, os.path.join(self.args.unified_image_path,image_path.name))


    def main(self):

        self.image_path_check()
        self.image_merge()
        self.category_merge()
        self.annotation_merge()
        self.save_json()
        
        self.image_move()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--base_json", type=str, default='coco_custom1/annotations/sample_annotation1.json', help="Base json path")
    parser.add_argument("--base_image_path", type=str, default='coco_custom1/images/', help="Base images folder")

    parser.add_argument("--add_json", type=str, default='coco_custom2/annotations/sample_annotation2.json', help="Added json path")
    parser.add_argument("--add_image_path", type=str, default='coco_custom2/images/', help="Added images folder")

    parser.add_argument("--unified_json_path", type=str, default='coco_merge/annotations/merge_annotation.json', help="Unified json Save Path")
    parser.add_argument("--unified_image_path", type=str, default='coco_merge/images/ ', help="Unified images Save folder")

    args = parser.parse_args()
    
    main = MergeAnnotation(args)
    main.main()