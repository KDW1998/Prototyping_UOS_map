#!/usr/bin/env python3
"""
Super Resolution for Image Enhancement
초해상화를 통한 이미지 품질 향상

Usage:
    python super_resolution.py --model-name edsr --model-config '모델/초해상화/초해상화_config.py' \
        --model-ckpt '모델/초해상화/초해상화_weight.pth' --img-dir '/home/user/WindowsShare/02. Projects/2025.03 프로토타이핑사업/test_data_LR(training)/2023_현장촬영이미지_학습용데이터셋/LR/leftImg8bit/train' --result-out-dir '/home/user/WindowsShare/02. Projects/2025.03 프로토타이핑사업/test_data_LR(training)/2023_현장촬영이미지_학습용데이터셋/SR/leftImg8bit/train'
"""

from argparse import ArgumentParser
from mmengine import DictAction
from mmagic.apis import MMagicInferencer
import os

def parse_args():
    parser = ArgumentParser(description='Super Resolution using MMagic')
    parser.add_argument(
        '--img', type=str, default=None, help='Input image file.')
    parser.add_argument(
        '--video', type=str, default=None, help='Input video file.')
    parser.add_argument('--img-dir', type=str, default=None, help='Input directory containing images to be processed.')
    parser.add_argument(
        '--label',
        type=int,
        default=None,
        help='Input label for conditional models.')
    parser.add_argument(
        '--trimap', type=str, default=None, help='Input for matting models.')
    parser.add_argument(
        '--mask',
        type=str,
        default=None,
        help='path to input mask file for inpainting models')
    parser.add_argument(
        '--text',
        type=str,
        default='',
        help='text input for text2image models')
    parser.add_argument(
        '--result-out-dir',
        type=str,
        default=None,
        help='Output img or video path.')
    parser.add_argument(
        '--model-name',
        type=str,
        default=None,
        help='Pretrained mmagic algorithm')
    parser.add_argument(
        '--model-setting',
        type=int,
        default=None,
        help='Pretrained mmagic algorithm setting')
    parser.add_argument(
        '--model-config',
        type=str,
        default=None,
        help='Path to the custom config file of the selected mmagic model.')
    parser.add_argument(
        '--model-ckpt',
        type=str,
        default=None,
        help='Path to the custom checkpoint file of the selected det model.')
    parser.add_argument(
        '--device',
        type=str,
        default='cuda',
        help='Device used for inference.')
    parser.add_argument(
        '--extra-parameters',
        nargs='+',
        action=DictAction,
        help='Other customized kwargs for different model')
    parser.add_argument(
        '--seed',
        type=int,
        default=2022,
        help='The random seed used in inference.')
    # print supported tasks and models
    parser.add_argument(
        '--print-supported-models',
        action='store_true',
        help='print all supported models for inference.')
    parser.add_argument(
        '--print-supported-tasks',
        action='store_true',
        help='print all supported tasks for inference.')
    parser.add_argument(
        '--print-task-supported-models',
        type=str,
        default=None,
        help='print all supported models for one task')

    args, unknown = parser.parse_known_args()

    return args, unknown


def main():
    args, unknown = parse_args()
    assert len(unknown) % 2 == 0, (
        'User defined arguments must be passed in pair, but receive '
        f'{len(unknown)} arguments.')

    user_defined = {}
    for idx in range(len(unknown) // 2):
        key, val = unknown[idx * 2], unknown[idx * 2 + 1]
        assert key.startswith('--'), (
            'Key of user define arguments must be start with \'--\', but '
            f'receive \'{key}\'.')

        key = key.replace('-', '_')
        val = int(val) if val.isdigit() else val
        user_defined[key[2:]] = val

    user_defined.update(vars(args))

    if args.print_supported_models:
        inference_supported_models = \
            MMagicInferencer.get_inference_supported_models()
        print('all supported models:')
        print(inference_supported_models)
        return

    if args.print_supported_tasks:
        supported_tasks = MMagicInferencer.get_inference_supported_tasks()
        print('all supported tasks:')
        print(supported_tasks)
        return

    if args.print_task_supported_models:
        task_supported_models = \
            MMagicInferencer.get_task_supported_models(
                args.print_task_supported_models)
        print('translation models:')
        print(task_supported_models)
        return
    
    print("="*60)
    print("Super Resolution Processing")
    print("="*60)
    
    # Check if img-dir is provided and process all images in that directory
    if args.img_dir:
        # Ensure the input directory exists
        assert os.path.isdir(args.img_dir), f"'{args.img_dir}' is not a valid directory."
        
        # Ensure output directory exists
        os.makedirs(args.result_out_dir, exist_ok=True)
        
        # Get all image files
        image_files = sorted([f for f in os.listdir(args.img_dir) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        print(f"\nFound {len(image_files)} images to process")
        print(f"Input: {args.img_dir}")
        print(f"Output: {args.result_out_dir}")
        print(f"Model: {args.model_name}")
        print("")
        
        # Initialize the inferencer (without img-dir parameter)
        init_args = vars(args).copy()
        init_args['img_dir'] = None  # Remove img_dir from initialization
        editor = MMagicInferencer(**init_args)
        
        # Process each image individually
        for idx, img_name in enumerate(image_files, 1):
            img_path = os.path.join(args.img_dir, img_name)
            output_path = os.path.join(args.result_out_dir, img_name)
            print(f"[{idx}/{len(image_files)}] Processing: {img_name}")
            
            # Infer for single image with explicit output path
            result = editor.infer(img=img_path)
            
            # Save result manually
            import cv2
            cv2.imwrite(output_path, result[1])
            print(f"Saved: {output_path}")
        
        print(f"\nSuper resolution processing completed.")
        print(f"Processed {len(image_files)} images")
    else:
        # Process single image or video
        editor = MMagicInferencer(**vars(args))
        editor.infer(**user_defined)

if __name__ == '__main__':
    main()

