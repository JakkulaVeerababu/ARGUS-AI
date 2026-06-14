import os
import sys
import importlib.util
from typing import List


class LocalSubmissionValidator:
    @staticmethod
    def validate(csv_path: str) -> bool:
        """
        Loads the hidden/official validate_submission.py module dynamically
        and validates the generated CSV file.
        """
        # Search path
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        official_validator_path = os.path.abspath(
            os.path.join(base_dir, "data/validate_submission.py")
        )

        if not os.path.exists(official_validator_path):
            # Try nested folder path
            official_validator_path = os.path.abspath(
                os.path.join(
                    base_dir,
                    "[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py",
                )
            )

        if not os.path.exists(official_validator_path):
            print("Error: Official validator not found at expected paths.")
            return False

        print(f"Loading official validator from: {official_validator_path}")

        # Load module dynamically
        spec = importlib.util.spec_from_file_location(
            "validate_submission", official_validator_path
        )
        validator_module = importlib.util.module_from_spec(spec)
        sys.modules["validate_submission"] = validator_module
        spec.loader.exec_module(validator_module)

        # Run validation
        errors: List[str] = validator_module.validate_submission(csv_path)

        if errors:
            print(f"Validation FAILED ({len(errors)} issues):")
            for err in errors:
                print(f"  - {err}")
            return False

        print("Validation PASSED. Submission file is completely valid!")
        return True


if __name__ == "__main__":
    # Test on a dummy path or show usage
    if len(sys.argv) > 1:
        LocalSubmissionValidator.validate(sys.argv[1])
    else:
        print(
            "Usage: python -m backend.app.reasoning.submission_validator <path_to_submission.csv>"
        )
