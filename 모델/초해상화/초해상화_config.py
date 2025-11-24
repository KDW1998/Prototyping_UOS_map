custom_hooks = [
    dict(interval=1, type='BasicVisualizationHook'),
]
data_root = '/home/user/WindowsShare/05. Data/04. Raw Images & Archive/206.hardnegative/SuperResolution/SRCrack_HNS/leftImg8bit'
dataset_type = 'BasicImageDataset'
default_hooks = dict(
    checkpoint=dict(
        by_epoch=False,
        interval=5000,
        max_keep_ckpts=10,
        out_dir='./work_dirs/',
        rule='greater',
        save_best='PSNR',
        save_optimizer=True,
        type='CheckpointHook'),
    logger=dict(interval=100, type='LoggerHook'),
    param_scheduler=dict(type='ParamSchedulerHook'),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    timer=dict(type='IterTimerHook'))
default_scope = 'mmagic'
div2k_data_root = 'data/DIV2K'
div2k_dataloader = dict(
    dataset=dict(
        ann_file='meta_info_DIV2K100sub_GT.txt',
        data_prefix=dict(
            gt='DIV2K_train_HR_sub', img='DIV2K_train_LR_bicubic/X4_sub'),
        data_root='data/DIV2K',
        metainfo=dict(dataset_type='div2k', task_name='sisr'),
        pipeline=[
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='img',
                type='LoadImageFromFile'),
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='gt',
                type='LoadImageFromFile'),
            dict(type='PackInputs'),
        ],
        type='BasicImageDataset'),
    drop_last=False,
    num_workers=4,
    persistent_workers=False,
    sampler=dict(shuffle=False, type='DefaultSampler'))
div2k_evaluator = dict(
    metrics=[
        dict(crop_border=4, prefix='DIV2K', type='PSNR'),
        dict(crop_border=4, prefix='DIV2K', type='SSIM'),
    ],
    type='Evaluator')
env_cfg = dict(
    cudnn_benchmark=False,
    dist_cfg=dict(backend='nccl'),
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=4))
experiment_name = 'edsr_x4c64b16_1xb16-300k_div2k'
launcher = 'pytorch'
load_from = None
log_level = 'INFO'
log_processor = dict(by_epoch=False, type='LogProcessor', window_size=100)
model = dict(
    data_preprocessor=dict(
        mean=[
            0.0,
            0.0,
            0.0,
        ],
        std=[
            255.0,
            255.0,
            255.0,
        ],
        type='DataPreprocessor'),
    generator=dict(
        in_channels=3,
        mid_channels=64,
        num_blocks=16,
        out_channels=3,
        res_scale=1,
        rgb_mean=[
            0.4488,
            0.4371,
            0.404,
        ],
        rgb_std=[
            1.0,
            1.0,
            1.0,
        ],
        type='EDSRNet',
        upscale_factor=4),
    pixel_loss=dict(loss_weight=1.0, reduction='mean', type='L1Loss'),
    test_cfg=dict(crop_border=4, metrics=[
        'PSNR',
    ]),
    train_cfg=dict(),
    type='BaseEditModel')
optim_wrapper = dict(
    constructor='DefaultOptimWrapperConstructor',
    optimizer=dict(betas=(
        0.9,
        0.999,
    ), lr=0.0001, type='Adam'),
    type='OptimWrapper')
param_scheduler = dict(
    by_epoch=False, gamma=0.5, milestones=[
        200000,
    ], type='MultiStepLR')
resume = False
save_dir = './work_dirs/'
scale = 4
set14_data_root = 'data/Set14'
set14_dataloader = dict(
    dataset=dict(
        data_prefix=dict(gt='GTmod12', img='LRbicx4'),
        data_root='data/Set14',
        metainfo=dict(dataset_type='set14', task_name='sisr'),
        pipeline=[
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='img',
                type='LoadImageFromFile'),
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='gt',
                type='LoadImageFromFile'),
            dict(type='PackInputs'),
        ],
        type='BasicImageDataset'),
    drop_last=False,
    num_workers=4,
    persistent_workers=False,
    sampler=dict(shuffle=False, type='DefaultSampler'))
set14_evaluator = dict(
    metrics=[
        dict(crop_border=4, prefix='Set14', type='PSNR'),
        dict(crop_border=4, prefix='Set14', type='SSIM'),
    ],
    type='Evaluator')
set5_data_root = 'data/Set5'
set5_dataloader = dict(
    dataset=dict(
        data_prefix=dict(gt='GTmod12', img='LRbicx4'),
        data_root='data/Set5',
        metainfo=dict(dataset_type='set5', task_name='sisr'),
        pipeline=[
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='img',
                type='LoadImageFromFile'),
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='gt',
                type='LoadImageFromFile'),
            dict(type='PackInputs'),
        ],
        type='BasicImageDataset'),
    drop_last=False,
    num_workers=4,
    persistent_workers=False,
    sampler=dict(shuffle=False, type='DefaultSampler'))
set5_evaluator = dict(
    metrics=[
        dict(crop_border=4, prefix='Set5', type='PSNR'),
        dict(crop_border=4, prefix='Set5', type='SSIM'),
    ],
    type='Evaluator')
test_cfg = dict(type='MultiTestLoop')
test_dataloader = [
    dict(
        dataset=dict(
            data_prefix=dict(gt='GTmod12', img='LRbicx4'),
            data_root='data/Set5',
            metainfo=dict(dataset_type='set5', task_name='sisr'),
            pipeline=[
                dict(
                    channel_order='rgb',
                    color_type='color',
                    imdecode_backend='cv2',
                    key='img',
                    type='LoadImageFromFile'),
                dict(
                    channel_order='rgb',
                    color_type='color',
                    imdecode_backend='cv2',
                    key='gt',
                    type='LoadImageFromFile'),
                dict(type='PackInputs'),
            ],
            type='BasicImageDataset'),
        drop_last=False,
        num_workers=4,
        persistent_workers=False,
        sampler=dict(shuffle=False, type='DefaultSampler')),
    dict(
        dataset=dict(
            data_prefix=dict(gt='GTmod12', img='LRbicx4'),
            data_root='data/Set14',
            metainfo=dict(dataset_type='set14', task_name='sisr'),
            pipeline=[
                dict(
                    channel_order='rgb',
                    color_type='color',
                    imdecode_backend='cv2',
                    key='img',
                    type='LoadImageFromFile'),
                dict(
                    channel_order='rgb',
                    color_type='color',
                    imdecode_backend='cv2',
                    key='gt',
                    type='LoadImageFromFile'),
                dict(type='PackInputs'),
            ],
            type='BasicImageDataset'),
        drop_last=False,
        num_workers=4,
        persistent_workers=False,
        sampler=dict(shuffle=False, type='DefaultSampler')),
    dict(
        dataset=dict(
            ann_file='meta_info_DIV2K100sub_GT.txt',
            data_prefix=dict(
                gt='DIV2K_train_HR_sub', img='DIV2K_train_LR_bicubic/X4_sub'),
            data_root='data/DIV2K',
            metainfo=dict(dataset_type='div2k', task_name='sisr'),
            pipeline=[
                dict(
                    channel_order='rgb',
                    color_type='color',
                    imdecode_backend='cv2',
                    key='img',
                    type='LoadImageFromFile'),
                dict(
                    channel_order='rgb',
                    color_type='color',
                    imdecode_backend='cv2',
                    key='gt',
                    type='LoadImageFromFile'),
                dict(type='PackInputs'),
            ],
            type='BasicImageDataset'),
        drop_last=False,
        num_workers=4,
        persistent_workers=False,
        sampler=dict(shuffle=False, type='DefaultSampler')),
]
test_evaluator = [
    dict(
        metrics=[
            dict(crop_border=4, prefix='Set5', type='PSNR'),
            dict(crop_border=4, prefix='Set5', type='SSIM'),
        ],
        type='Evaluator'),
    dict(
        metrics=[
            dict(crop_border=4, prefix='Set14', type='PSNR'),
            dict(crop_border=4, prefix='Set14', type='SSIM'),
        ],
        type='Evaluator'),
    dict(
        metrics=[
            dict(crop_border=4, prefix='DIV2K', type='PSNR'),
            dict(crop_border=4, prefix='DIV2K', type='SSIM'),
        ],
        type='Evaluator'),
]
test_pipeline = [
    dict(
        channel_order='rgb',
        color_type='color',
        imdecode_backend='cv2',
        key='img',
        type='LoadImageFromFile'),
    dict(
        channel_order='rgb',
        color_type='color',
        imdecode_backend='cv2',
        key='gt',
        type='LoadImageFromFile'),
    dict(type='PackInputs'),
]
train_cfg = dict(
    max_iters=120000, type='IterBasedTrainLoop', val_interval=1000)
train_dataloader = dict(
    batch_size=16,
    dataset=dict(
        ann_file=
        '/home/user/WindowsShare/05. Data/04. Raw Images & Archive/206.hardnegative/SuperResolution/SRCrack_HNS/leftImg8bit/train/meta_info_train.txt',
        data_prefix=dict(gt='train/HR', img='train/LR'),
        data_root=
        '/home/user/WindowsShare/05. Data/04. Raw Images & Archive/206.hardnegative/SuperResolution/SRCrack_HNS/leftImg8bit',
        filename_tmpl=dict(gt='{}', img='{}'),
        metainfo=dict(dataset_type='div2k', task_name='sisr'),
        pipeline=[
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='img',
                type='LoadImageFromFile'),
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='gt',
                type='LoadImageFromFile'),
            dict(dictionary=dict(scale=4), type='SetValues'),
            dict(gt_patch_size=196, type='PairedRandomCrop'),
            dict(
                direction='horizontal',
                flip_ratio=0.5,
                keys=[
                    'img',
                    'gt',
                ],
                type='Flip'),
            dict(
                direction='vertical',
                flip_ratio=0.5,
                keys=[
                    'img',
                    'gt',
                ],
                type='Flip'),
            dict(
                keys=[
                    'img',
                    'gt',
                ],
                transpose_ratio=0.5,
                type='RandomTransposeHW'),
            dict(type='PackInputs'),
        ],
        type='BasicImageDataset'),
    drop_last=True,
    num_workers=8,
    persistent_workers=False,
    sampler=dict(shuffle=True, type='InfiniteSampler'))
train_pipeline = [
    dict(
        channel_order='rgb',
        color_type='color',
        imdecode_backend='cv2',
        key='img',
        type='LoadImageFromFile'),
    dict(
        channel_order='rgb',
        color_type='color',
        imdecode_backend='cv2',
        key='gt',
        type='LoadImageFromFile'),
    dict(dictionary=dict(scale=4), type='SetValues'),
    dict(gt_patch_size=196, type='PairedRandomCrop'),
    dict(
        direction='horizontal',
        flip_ratio=0.5,
        keys=[
            'img',
            'gt',
        ],
        type='Flip'),
    dict(
        direction='vertical',
        flip_ratio=0.5,
        keys=[
            'img',
            'gt',
        ],
        type='Flip'),
    dict(keys=[
        'img',
        'gt',
    ], transpose_ratio=0.5, type='RandomTransposeHW'),
    dict(type='PackInputs'),
]
val_cfg = dict(type='MultiValLoop')
val_dataloader = dict(
    dataset=dict(
        data_prefix=dict(gt='val/HR', img='val/LR'),
        data_root=
        '/home/user/WindowsShare/05. Data/04. Raw Images & Archive/206.hardnegative/SuperResolution/SRCrack_HNS/leftImg8bit',
        metainfo=dict(dataset_type='set5', task_name='sisr'),
        pipeline=[
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='img',
                type='LoadImageFromFile'),
            dict(
                channel_order='rgb',
                color_type='color',
                imdecode_backend='cv2',
                key='gt',
                type='LoadImageFromFile'),
            dict(type='PackInputs'),
        ],
        type='BasicImageDataset'),
    drop_last=False,
    num_workers=4,
    persistent_workers=False,
    sampler=dict(shuffle=False, type='DefaultSampler'))
val_evaluator = dict(
    metrics=[
        dict(type='MAE'),
        dict(crop_border=4, type='PSNR'),
        dict(crop_border=4, type='SSIM'),
    ],
    type='Evaluator')
val_pipeline = [
    dict(
        channel_order='rgb',
        color_type='color',
        imdecode_backend='cv2',
        key='img',
        type='LoadImageFromFile'),
    dict(
        channel_order='rgb',
        color_type='color',
        imdecode_backend='cv2',
        key='gt',
        type='LoadImageFromFile'),
    dict(type='PackInputs'),
]
vis_backends = [
    dict(type='LocalVisBackend'),
]
visualizer = dict(
    bgr2rgb=True,
    fn_key='gt_path',
    img_keys=[
        'gt_img',
        'input',
        'pred_img',
    ],
    type='ConcatImageVisualizer',
    vis_backends=[
        dict(type='LocalVisBackend'),
    ])
work_dir = './work_dirs/edsr_x4c64b16_1xb16-300k_div2k'
