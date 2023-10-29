from transformers import AutoTokenizer, AutoModel
import torch
import time
import os

torch.cuda.empty_cache()

os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:200'

if __name__ == '__main__':
    start_time = time.time()
    tokenizer = AutoTokenizer.from_pretrained("THUDM/codegeex2-6b", trust_remote_code=True)
    model = AutoModel.from_pretrained("THUDM/codegeex2-6b", trust_remote_code=True, low_cpu_mem_usage=True,
                                      device="cuda")
    model = model.eval()

    # remember adding a language tag for better performance
    prompt = "# language: python\n# write a function to generate response from openai API Chat Completion\n"
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(inputs, max_length=256, top_k=1)
    response = tokenizer.decode(outputs[0])

    print(response)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed time: %.2f seconds" % elapsed_time)
