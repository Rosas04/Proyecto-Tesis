import pytest
import zipfile
from unittest.mock import patch, MagicMock
from pathlib import Path
from services.zip_service import extract_zip_project

@patch("services.zip_service.zipfile.ZipFile")
@patch("services.zip_service.Path.mkdir")
@patch("services.zip_service.shutil.rmtree")
@patch("services.zip_service._collect_files")
@patch("services.zip_service._detect_project_type")
@patch("services.zip_service._build_combined_css")
@patch("services.zip_service._build_interfaces")
@patch("services.zip_service._build_combined_html")
def test_extract_and_filter(
    mock_build_combined_html,
    mock_build_interfaces,
    mock_build_combined_css,
    mock_detect_project_type,
    mock_collect_files,
    mock_rmtree,
    mock_mkdir,
    mock_zipfile_class
):
    # Prepare the mock zip file and its contents
    mock_zip_instance = MagicMock()
    mock_zipfile_class.return_value.__enter__.return_value = mock_zip_instance
    
    # Create mock zip info objects
    # 1. Valid frontend file
    mock_valid_file = MagicMock()
    mock_valid_file.is_dir.return_value = False
    mock_valid_file.filename = "src/index.html"
    
    # 2. Ignored directory file (.git)
    mock_ignored_git = MagicMock()
    mock_ignored_git.is_dir.return_value = False
    mock_ignored_git.filename = ".git/config"
    
    # 3. Ignored directory file (node_modules)
    mock_ignored_node = MagicMock()
    mock_ignored_node.is_dir.return_value = False
    mock_ignored_node.filename = "node_modules/package/index.js"
    
    # 4. Directory itself
    mock_dir = MagicMock()
    mock_dir.is_dir.return_value = True
    mock_dir.filename = "src/"
    
    mock_zip_instance.infolist.return_value = [
        mock_valid_file, mock_ignored_git, mock_ignored_node, mock_dir
    ]
    
    # Mock subsequent steps to just return empty or default values to pass the flow
    mock_collect_files.return_value = {
        "src/index.html": {
            "file_name": "index.html",
            "path": "extracted_projects_temp/src/index.html",
            "relative_path": "src/index.html",
            "extension": ".html",
            "content": "<html></html>",
            "size": 13
        }
    }
    mock_detect_project_type.return_value = "vanilla"
    mock_build_combined_css.return_value = ""
    mock_build_interfaces.return_value = []
    mock_build_combined_html.return_value = ""
    
    # Call the function
    result = extract_zip_project("dummy.zip")
    
    # Assertions
    # Ensure extract was called ONLY for the valid file
    mock_zip_instance.extract.assert_called_once_with(mock_valid_file, Path("extracted_projects_temp").resolve())
    
    # Ensure success status
    assert result["status"] == "extracted"
    assert result["project_type"] == "vanilla"
