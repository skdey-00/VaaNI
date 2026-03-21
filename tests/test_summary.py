"""
Summary and PDF export integration tests.

Tests session summary generation and PDF export functionality.
"""

import pytest
import requests
import base64
from pathlib import Path
import time


@pytest.mark.integration
def test_session_summary_bilingual(test_services, http_client, test_session):
    """Test that session summary returns both English and customer language text."""
    session_id = test_session

    # Add some transcript entries first
    # (In a real test, you would send audio through WebSocket)
    # For now, we'll just test the endpoint structure

    # End the session to generate summary
    response = http_client.post(f"{test_services['gateway']}/session/{session_id}/end")

    assert response.status_code == 200
    data = response.json()

    # Assert response shape
    assert "summary_en" in data
    assert "summary_lang" in data
    assert "query_type" in data

    # Assert both summaries exist
    assert len(data["summary_en"]) > 0, "English summary should not be empty"
    assert len(data["summary_lang"]) > 0, "Customer language summary should not be empty"

    # Assert query type exists
    assert len(data["query_type"]) > 0

    print(f"✅ Bilingual summary generated:")
    print(f"  English: {data['summary_en'][:100]}...")
    print(f"  Local: {data['summary_lang'][:100]}...")
    print(f"  Query Type: {data['query_type']}")


@pytest.mark.integration
def test_session_transcript(test_services, http_client, test_session):
    """Test fetching full transcript."""
    session_id = test_session

    # Get transcript
    response = http_client.get(f"{test_services['gateway']}/session/{session_id}/transcript")

    assert response.status_code == 200
    data = response.json()

    # Assert response shape
    assert "transcript" in data
    assert isinstance(data["transcript"], list)

    print(f"✅ Transcript retrieved: {len(data['transcript'])} entries")


@pytest.mark.integration
def test_pdf_export(test_services, http_client, test_session):
    """Test PDF export endpoint returns valid PDF."""
    session_id = test_session

    # End session first to ensure summary exists
    http_client.post(f"{test_services['gateway']}/session/{session_id}/end")

    # Export PDF
    response = http_client.get(f"{test_services['gateway']}/session/{session_id}/export/pdf")

    assert response.status_code == 200

    # Assert content type is PDF
    content_type = response.headers.get("content-type", "")
    assert "application/pdf" in content_type, f"Expected PDF content-type, got: {content_type}"

    # Assert content disposition has filename
    content_disposition = response.headers.get("content-disposition", "")
    assert "filename" in content_disposition, "PDF should have filename in Content-Disposition"

    # Assert PDF content is not empty
    pdf_content = response.content
    assert len(pdf_content) > 1000, "PDF content should be substantial"

    # Check PDF magic bytes (%PDF)
    assert pdf_content[:4] == b"%PDF", "Should start with PDF magic bytes"

    print(f"✅ PDF exported successfully: {len(pdf_content)} bytes")
    print(f"  Content-Type: {content_type}")
    print(f"  Content-Disposition: {content_disposition}")


@pytest.mark.integration
def test_json_export(test_services, http_client, test_session):
    """Test JSON export returns structured session data."""
    session_id = test_session

    # Export JSON
    response = http_client.post(
        f"{test_services['gateway']}/session/{session_id}/export/json"
    )

    assert response.status_code == 200

    # Assert content type is JSON
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type, f"Expected JSON content-type, got: {content_type}"

    # Parse JSON
    data = response.json()

    # Assert required fields
    assert "session_id" in data
    assert "created_at" in data
    assert "transcript" in data
    assert "metadata" in data

    # Assert transcript is a list
    assert isinstance(data["transcript"], list)

    # Assert metadata exists
    assert "branch_code" in data["metadata"]
    assert "staff_id" in data["metadata"]

    print(f"✅ JSON exported successfully")
    print(f"  Session ID: {data['session_id']}")
    print(f"  Transcript entries: {len(data['transcript'])}")


@pytest.mark.integration
def test_session_lifecycle(test_services, http_client):
    """Test complete session lifecycle: start → use → end → export."""
    # Step 1: Start session
    start_response = http_client.post(f"{test_services['gateway']}/session/start")
    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]
    print(f"Step 1: Started session {session_id}")

    # Step 2: Check session exists
    list_response = http_client.get(f"{test_services['gateway']}/sessions")
    assert list_response.status_code == 200
    sessions = list_response.json()["sessions"]
    session_ids = [s["session_id"] for s in sessions]
    assert session_id in session_ids
    print(f"Step 2: Session found in active list")

    # Step 3: Get transcript (should be empty)
    transcript_response = http_client.get(
        f"{test_services['gateway']}/session/{session_id}/transcript"
    )
    assert transcript_response.status_code == 200
    transcript = transcript_response.json()["transcript"]
    assert isinstance(transcript, list)
    print(f"Step 3: Transcript has {len(transcript)} entries")

    # Step 4: End session
    end_response = http_client.post(
        f"{test_services['gateway']}/session/{session_id}/end"
    )
    assert end_response.status_code == 200
    summary = end_response.json()
    assert "summary_en" in summary
    assert "summary_lang" in summary
    print(f"Step 4: Session ended, summary generated")

    # Step 5: Export PDF
    pdf_response = http_client.get(
        f"{test_services['gateway']}/session/{session_id}/export/pdf"
    )
    assert pdf_response.status_code == 200
    assert pdf_response.headers.get("content-type", "").startswith("application/pdf")
    print(f"Step 5: PDF exported ({len(pdf_response.content)} bytes)")

    # Step 6: Export JSON
    json_response = http_client.post(
        f"{test_services['gateway']}/session/{session_id}/export/json"
    )
    assert json_response.status_code == 200
    json_data = json_response.json()
    assert json_data["session_id"] == session_id
    print(f"Step 6: JSON exported")

    # Step 7: Delete session
    delete_response = http_client.delete(
        f"{test_services['gateway']}/session/{session_id}"
    )
    assert delete_response.status_code == 200
    print(f"Step 7: Session deleted")

    print("✅ Complete session lifecycle test passed!")


@pytest.mark.integration
def test_multiple_concurrent_sessions(test_services, http_client):
    """Test handling multiple concurrent sessions."""
    session_ids = []

    # Create 3 sessions
    for i in range(3):
        response = http_client.post(f"{test_services['gateway']}/session/start")
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        session_ids.append(session_id)
        print(f"Created session {i+1}: {session_id}")

    # Verify all are in the list
    list_response = http_client.get(f"{test_services['gateway']}/sessions")
    assert list_response.status_code == 200
    sessions = list_response.json()["sessions"]
    active_ids = [s["session_id"] for s in sessions]

    for session_id in session_ids:
        assert session_id in active_ids

    print(f"✅ All {len(session_ids)} sessions are active")

    # Clean up
    for session_id in session_ids:
        http_client.delete(f"{test_services['gateway']}/session/{session_id}")

    print("✅ Concurrent sessions test passed")
