import torch.nn as nn


class SignalNet(nn.Module): # [51, 129] -> [N]

    def __init__(self, num_of_class):
        super(SignalNet, self).__init__()

        self.model = nn.Sequential(
            nn.Conv1d(51, 64, kernel_size=3, stride=1, padding=1),
            nn.MaxPool1d(2),

            nn.Conv1d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.MaxPool1d(2),

            nn.Conv1d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.MaxPool1d(2),

        )

        self.linear = nn.Sequential(
            nn.Linear(4096 ,1024),
            nn.LeakyReLU(inplace=True),
            nn.Linear(1024, num_of_class),
        )

    def forward(self,x):
        x = self.model(x)
        x = x.view(x.size(0), -1)
        x = self.linear(x)

        return x
