# Rekognition Discord Bot

Rekognition Discord Bot leverages the power of AWS Rekognition to analyze and compare images directly from Discord. With a simple command, you can identify objects, detect emotions, recognize celebrities, read text, and even compare faces in two different images!

## Table of Contents
- [Features](#features)
- [Setup](#setup)
  - [AWS Configuration](#aws-configuration)
  - [Discord Bot Configuration](#discord-bot-configuration)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Object and Scene Detection**: Identify thousands of objects such as a bicycle or sunglasses.
- **Emotion Detection**: Understand the sentiment behind a face like happiness, sadness, or surprise.
- **Celebrity Recognition**: Recognize thousands of celebrities in images.
- **Text Detection**: Extract text from the image.
- **Face Comparison**: Compare two faces to see if they are of the same person.

## Setup

### AWS Configuration

1. **Sign Up for AWS**: If you do not have an AWS account, you need to sign up [here](https://aws.amazon.com/).
2. **Set up an IAM user**:
   - Sign in to the AWS Management Console and open the IAM console.
   - In the navigation pane, choose Users, and then choose Add user.
   - Set the user name and choose Programmatic access. This provides an access key ID and secret access key for the AWS API, CLI, SDK, and other development tools.
   - Set permissions by attaching the policy: `AmazonRekognitionFullAccess`.
   - Review and create the user. Note down the access key ID and secret access key.
3. (Optional) **Change the default region**: By default, this bot is configured to use the `us-west-1` region. To use a different region, you can modify the `region_name` in the bot code.

### Discord Bot Configuration

1. **Clone the Repository**:
   ```
   git clone https://github.com/RocketGod-git/rekognition-bot.git
   cd rekognition-bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install discord boto3
   ```

3. **Configure the Bot**:
   - Edit `config.json`.
   - Fill in the `TOKEN`, `AWS_ACCESS_KEY`, and `AWS_SECRET_KEY` in the `config.json` with your Discord bot token and AWS credentials respectively.

## Usage

1. **Run the Bot**:
   ```bash
   python main.py
   ```

2. **In Discord**:
   - Use the command `/photos` followed by attaching a photo to analyze it.
   - Attach a second photo to compare faces between the two images.

## Examples

- **Analyzing a Photo**:
   `/photos`
  
![mclaren](https://github.com/RocketGod-git/rekognition-bot/assets/57732082/2a9936e3-e7ea-4c55-bbd6-c2a9186df686)


![George_Clooney](https://github.com/RocketGod-git/rekognition-bot/assets/57732082/41423222-5eb4-4800-be26-92c6a3e99116)

   Bot will return details about the image, such as objects detected, any celebrities recognized, emotions of faces, and more.

- **Comparing Faces in Two Photos**:
   `/photos`

![Usama_Bin_Laden](https://github.com/RocketGod-git/rekognition-bot/assets/57732082/54755638-d7be-4a53-a0c1-1dc99ebd4a10)

   Bot will compare the faces in the two images and provide a similarity score.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [AGPL-3.0 license](https://github.com/RocketGod-git/rekognition-bot/blob/main/LICENSE).

![rocketgod_logo](https://github.com/RocketGod-git/shodanbot/assets/57732082/7929b554-0fba-4c2b-b22d-6772d23c4a18)
