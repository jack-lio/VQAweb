import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, 1, 1)
        self.bn1 = nn.BatchNorm2d(16)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 3, 1, 1)
        self.bn2 = nn.BatchNorm2d(32)

        with torch.no_grad():
            dummy = torch.zeros(1, 3, 128, 128)
            x = self.pool(F.relu(self.bn1(self.conv1(dummy))))
            x = self.pool(F.relu(self.bn2(self.conv2(x))))
            flatten_dim = x.view(1, -1).shape[1]

        self.fc1 = nn.Linear(flatten_dim, 128)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        return x

class TabularMLP(nn.Module):
    def __init__(self, input_size, hidden_size=128):
        super(TabularMLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        return x

class MultimodalNet(nn.Module):
    def __init__(self, tabular_input_size, output_size=6):
        super(MultimodalNet, self).__init__()
        self.cnn = CNN()
        self.tabular = TabularMLP(tabular_input_size)
        self.fc = nn.Sequential(
            nn.Linear(128 + 128, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, output_size)
        )

    def forward(self, image, sensor_data):
        image_feat = self.cnn(image)
        tabular_feat = self.tabular(sensor_data)
        combined = torch.cat((image_feat, tabular_feat), dim=1)
        return self.fc(combined)

# === 儲存模型 ===
'''model = MultimodalNet(tabular_input_size=5)
torch.save(model.state_dict(), "model_A.pkl")
print("✅ 已儲存 model_A.pkl")'''