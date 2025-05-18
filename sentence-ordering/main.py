from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from src.evaluate import sample_evaluate
from src.train import prepare_trainer
from src.data import load_data

DATASET_PATH = 'data'
IS_CUDA      = 'cuda' if torch.cuda.is_available() else 'cpu'

model_name = "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-0.5B"
model      = AutoModelForCausalLM.from_pretrained(model_name).to(IS_CUDA)
tokenizer  = AutoTokenizer.from_pretrained(
                                            model_name, 
                                            model_max_length          = 2_048,
                                            truncation_side           = 'left',
                                            max_length                = 1_024,
                                            truncation                = True,  
                                            padding                   = "max_length",
                                        )

tokenizer.padding_size = 'right'
tokenizer.pad_token    = tokenizer.eos_token
model.tokenizer        = tokenizer

def train(**kwargs):

    train_dataset = load_data(
                        DATASET_PATH,
                        **kwargs
                    )
    
    print(f'sample data : {train_dataset["train"].data[0][0].as_py()}')

    trainer = prepare_trainer(model, train_dataset)
    trainer.train()

    trainer.save_model('output/adapter')
    trainer.tokenizer.save_pretrained('output/adapter/tokenizer')


if __name__ == '__main__':

    kwargs = {'has_context' : True}
    train(**kwargs)

    result = sample_evaluate(
                                base_model   = model, 
                                adapter_path = 'output/adapter'
                            )
    print(result)