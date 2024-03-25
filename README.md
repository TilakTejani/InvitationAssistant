# InvitationAssistant

## Connecting Selenium to an Already Running Chrome Browser

This guide explains how to configure Selenium to connect to an already running instance of Chrome browser through remote debugging. By following these steps, you can control an existing Chrome browser session using Selenium.

### Prerequisites

- [Google Chrome](https://www.google.com/chrome/) installed on your system.
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) installed and accessible on your system.
- Basic knowledge of using Selenium with Python.

### Steps

### 1. Start Chrome with Remote Debugging

Before connecting Selenium to an existing Chrome browser, you need to start Chrome with remote debugging enabled. Here’s how you can do it based on your operating system:

- **Windows**:
  ```shell
  "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

- **macOS**:
  ```shell
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222  
  ```

- **Linux**: 
    ```shell
    google-chrome --remote-debugging-port=9222
    ```

### 2. Starting Flask App

This guide explains how to start a Flask web application locally on your machine.

#### Prerequisites

- [Python](https://www.python.org/) installed on your system.
- Basic knowledge of Python and Flask.

#### Steps

##### 1. Clone the Repository

Clone the repository containing the Flask application code from the version control system (e.g., GitHub, GitLab, Bitbucket).

```bash
git clone <repository_url>
cd <repository_directory>
```

##### 2. Install Dependencies

Before running the Flask app, you need to install the required Python dependencies. These dependencies are listed in a file named `requirements.txt`.

To install the dependencies, open your terminal or command prompt, navigate to your project directory, and execute the following command:

```bash
pip install -r requirements.txt
```

This command will install all the required packages specified in the requirements.txt file.

Replace requirements.txt with the actual name of the requirements file if different.

##### 3. Run the Flask App

To run the Flask app, you need to execute the application entry point file using Python.

Running the App:

Navigate to your project directory in your terminal or command prompt, and execute the following command:

```bash
python app.py
```