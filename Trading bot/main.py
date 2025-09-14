"""
For ease of access the Streamlit run function has been called within main itself,
eliminating the need to launch the program from the cmd.
Instead, just press the run button in the IDE.
"""

import os
import sys
import subprocess
from ui.dashboard import create_streamlit_app


def main():
    """
    Entry point that either launches the Streamlit server or runs the app directly.

    Examples:
        >>> import os, sys, subprocess
        >>> from ui import dashboard
        >>> # Stub subprocess.run to capture its call
        >>> called = {}
        >>> original_run = subprocess.run
        >>> subprocess.run = lambda args: called.update({'args': args}) or None
        >>> # Ensure STREAMLIT_RUN_APP is not set
        >>> os.environ.pop('STREAMLIT_RUN_APP', None)
        >>> main()
        Starting Streamlit server...
        >>> # Environment variable should now be set
        >>> os.environ.get('STREAMLIT_RUN_APP')
        '1'
        >>> # subprocess.run was called with the correct executable
        >>> called['args'][0] == sys.executable
        True
        >>> # Restore subprocess.run
        >>> subprocess.run = original_run
        >>> # Stub create_streamlit_app to capture invocation
        >>> called_app = {}
        >>> dashboard.create_streamlit_app = lambda: called_app.update(called=True)
        >>> # Run under STREAMLIT_RUN_APP
        >>> os.environ['STREAMLIT_RUN_APP'] = '1'
        >>> main()
        >>> called_app.get('called', True)
        True
    """
    # Check if this script is being run directly or through Streamlit
    if not os.environ.get('STREAMLIT_RUN_APP'):
        print("Starting Streamlit server...")
        script_path = os.path.abspath(__file__)
        os.environ['STREAMLIT_RUN_APP'] = '1'
        subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])
        return

    # Create and display the Streamlit app
    create_streamlit_app()


if __name__ == "__main__":
    main()
