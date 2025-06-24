# modelaa.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class ImageTextClassifier(nn.Module):
    def __init__(self, num_classes, img_input_dim, text_input_dim, d_hid=64, en_att=False, att_name='', d_head=6):
        super(ImageTextClassifier, self).__init__()
        self.dropout_p = 0.1
        self.img_proj = nn.Sequential(
            nn.Linear(img_input_dim, d_hid),
            nn.ReLU(),
            nn.Dropout(self.dropout_p),
            nn.Linear(d_hid, d_hid)
        )
        self.text_proj = nn.Sequential(
            nn.Linear(text_input_dim, d_hid),
            nn.ReLU(),
            nn.Dropout(self.dropout_p),
            nn.Linear(d_hid, d_hid)
        )
        self.classifier = nn.Sequential(
            nn.Linear(d_hid * 2, 64),
            nn.ReLU(),
            nn.Dropout(self.dropout_p),
            nn.Linear(64, 1)
        )
        self.init_weight()

    def init_weight(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    m.bias.data.fill_(0.01)

    def forward(self, x_img, x_text):
        x_img = self.img_proj(x_img.mean(dim=1))
        if x_text.dim() == 3:
            x_text = x_text.mean(dim=1)
        x_text = self.text_proj(x_text)
        x_mm = torch.cat((x_img, x_text), dim=1)
        preds = self.classifier(x_mm)
        return preds, x_mm
