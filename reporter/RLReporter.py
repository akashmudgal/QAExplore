import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import base64

class RLReportGenerator:
    def __init__(self, report_path):
        self.report_path = report_path
        self.run_folder = None
        self.screenshots_folder = None
        self.report = {
            "run_start_time": "",
            "run_end_time": "",
            "episodes": []
        }
        self.current_episode = None
        self.episode_index = 0  # Track episode index

        # Create the report directory if it doesn't exist
        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)

    def _create_run_folder(self):
        """Create a folder for the current run and a subfolder for screenshots."""
        run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_folder = os.path.join(self.report_path, f"run_{run_timestamp}")
        os.makedirs(self.run_folder)
        self.screenshots_folder = os.path.join(self.run_folder, "screenshots")
        os.makedirs(self.screenshots_folder)

    def start_run(self):
        """Mark the start of the RL run and create the folder structure."""
        self.report["run_start_time"] = datetime.now().isoformat()
        self._create_run_folder()

    def end_run(self):
        """Mark the end of the RL run."""
        self.report["run_end_time"] = datetime.now().isoformat()

    def start_episode(self):
        """Start a new episode and increment episode index."""
        self.current_episode = {"steps": []}
        self.report["episodes"].append(self.current_episode)
        self.episode_index += 1  # Increment episode index

    def _save_image(self, base64_image, image_filename):
        """Save base64 image data as an image file in the screenshots folder."""
        image_path = os.path.join(self.screenshots_folder, image_filename)
        with open(image_path, 'wb') as img_file:
            img_file.write(base64.b64decode(base64_image))
        return os.path.relpath(image_path, self.run_folder)

    def add_step(self, state_name, state_image, action, action_image):
        """Add a step to the current episode."""
        # Include episode index in the filenames to make them unique across episodes
        state_image_filename = f"episode_{self.episode_index}_step_{len(self.current_episode['steps'])}_state_image.png"
        action_image_filename = f"episode_{self.episode_index}_step_{len(self.current_episode['steps'])}_action_image.png"

        # Save images to screenshots folder and get their relative paths
        state_image_path = self._save_image(state_image, state_image_filename)
        action_image_path = self._save_image(action_image, action_image_filename)

        # Add the step with references to saved images
        step = {
            "state": {
                "name": state_name,
                "image": state_image_path
            },
            "action": action,
            "action_image": action_image_path
        }
        self.current_episode["steps"].append(step)

    def generate_json(self):
        """Return the JSON report."""
        return json.dumps(self.report, indent=4)

    def generate_html_report(self, output_file='report.html'):
        """Generate the final HTML report using a Jinja2 template."""

        # Get the directory of the current script (where the template is located)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load the HTML template
        env = Environment(loader=FileSystemLoader(script_dir))
        template = env.get_template('report_template.html')

        # Render the template with the report data
        html_output = template.render(report=self.report)

        # Write the HTML to a file in the run folder
        output_html_path = os.path.join(self.run_folder, output_file)
        with open(output_html_path, 'w') as f:
            f.write(html_output)
        print(f"HTML report generated: {output_html_path}")
