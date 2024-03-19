from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
model = 'damo/nlp_structbert_sentence-similarity_chinese-base'


similarity_pipeline = pipeline(Tasks.sentence_similarity, )

content_a1 = """
模型采用了目前火热的 Diffusion Transformer (DiT) [1] 架构。作者团队以同样使用 DiT 架构的高质量开源文生图模型 PixArt-α [2] 为基座，在此基础上引入时间注意力层，将其扩展到了视频数据上。
具体来说，整个架构包括一个预训练好的 VAE，一个文本编码器，和一个利用空间 - 时间注意力机制的 STDiT (Spatial Temporal Diffusion Transformer) 模型。其中，STDiT 每层的结构如下图所示。
它采用串行的方式在二维的空间注意力模块上叠加一维的时间注意力模块，用于建模时序关系。在时间注意力模块之后，交叉注意力模块用于对齐文本的语意。
与全注意力机制相比，这样的结构大大降低了训练和推理开销。与同样使用空间 - 时间注意力机制的 Latte [3] 模型相比，STDiT 可以更好的利用已经预训练好的图像 DiT 的权重，从而在视频数据上继续训练。
"""

content_a2 = """
模型采用了Sora同源架构Diffusion Transformer (DiT) 。
它以采用DiT架构的高质量开源文生图模型PixArt-α为基座，在此基础上引入时间注意力层，将其扩展到视频数据上。
具体来看，整个架构包括一个预训练好的VAE，一个文本编码器和一个利用空间-时间注意力机制的STDiT (Spatial Temporal Diffusion Transformer)模型。
其中，STDiT 每层的结构如下图所示。
它采用串行的方式在二维的空间注意力模块上叠加一维的时间注意力模块，用于建模时序关系。在时间注意力模块之后，交叉注意力模块用于对齐文本的语意。
与全注意力机制相比，这样的结构大大降低了训练和推理开销。
与同样使用空间-时间注意力机制的 Latte模型相比，STDiT 可以更好的利用已经预训练好的图像 DiT 的权重，从而在视频数据上继续训练。
"""


result = similarity_pipeline(input=(content_a1, content_a2))

print(result)
