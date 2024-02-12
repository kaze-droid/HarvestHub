### Description
This gitlab repository is used to deploy a docker image containing two models used for image classification for vegetables. Each vegetable can be classified as one of 15 vegetables:
1. Bean
2. Bitter Gourd
3. Bottle Gourd
4. Brinjal
5. Broccoli
6. Cabbage
7. Capsicum
8. Carrot
9. Cauliflower
10. Cucumber
11. Papaya
12. Potato
13. Pumpkin
14. Radish
15. Tomato

### Models
There are two models deployed with one having an input of 31x31 and another of 128x128. The models managed to score an accuracy of 95.7% and 97.1% respectively on the test dataset. The models can be located at the following url:
- 31x31: https://vegetablecnn.onrender.com/v1/models/31x31
- 128x128: https://vegetablecnn.onrender.com/v1/models/128x128

### Notebook training
The training of the models are well-documented and can be found [here](https://nbviewer.org/github/kaze-droid/Vegetable-Image-Classification/blob/main/main.ipynb)