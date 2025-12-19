"""UAT Test Script for Supervisor and Agent Workflow.

Tests the full agent workflow: add a task and plan it using the Chat API.
"""

import os
import sys
from pathlib import Path

# Add src directory to path - noqa: E402
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# noqa: E402
from adhd_planner.utils.config import get_settings  # noqa: E402
from adhd_planner.utils.logger import get_logger  # noqa: E402

logger = get_logger("uat_test")


def test_supervisor_and_agents():
    """Test the full supervisor and agent workflow."""
    print("\n" + "=" * 60)
    print("UAT TEST: Supervisor and Agent Workflow")
    print("=" * 60)

    # Step 1: Initialize services
    print("\n[Step 1] Initializing services...")

    try:
        from adhd_planner.database.connection import get_db
        from adhd_planner.repositories.time_block_repository import TimeBlockRepository
        from adhd_planner.services.calendar_service import CalendarService
        from adhd_planner.services.llm_service import LLMService
        from adhd_planner.services.task_service import TaskService

        db = get_db()
        session = db.session_factory()

        task_service = TaskService(session)

        time_block_repository = TimeBlockRepository(session)
        calendar_service = CalendarService(time_block_repository)

        settings = get_settings()
        print(f"  - LLM Provider: {settings.llm_provider}")
        print(f"  - Database: {settings.database_path}")

        llm_service = LLMService()
        print("  - LLM Service initialized")
        print("  [OK] All services initialized successfully")

    except Exception as e:
        print(f"  [FAILED] Error initializing services: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 2: Build LangGraph
    print("\n[Step 2] Building LangGraph...")

    try:
        from adhd_planner.graph.builder import GraphBuilder

        builder = GraphBuilder(
            llm_service=llm_service,
            task_service=task_service,
            calendar_service=calendar_service,
        )
        graph = builder.build_graph()
        print("  [OK] LangGraph built successfully")

    except Exception as e:
        print(f"  [FAILED] Error building graph: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 3: Create ChatHandler
    print("\n[Step 3] Creating ChatHandler...")

    try:
        from adhd_planner.core.chat_handler import ChatHandler

        chat_handler = ChatHandler(graph=graph)
        print("  [OK] ChatHandler created")

    except Exception as e:
        print(f"  [FAILED] Error creating ChatHandler: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 4: Test adding a task
    print("\n[Step 4] Testing: Add a task...")
    print(
        "  User Input: 'Add task: Write unit tests for the calendar service, 2 hours, high priority'"
    )

    try:
        response = chat_handler.process_message(
            "Add task: Write unit tests for the calendar service, 2 hours, high priority"
        )
        print(f"\n  Agent Response:\n  {'-' * 50}")
        for line in response.split("\n"):
            print(f"  {line}")
        print(f"  {'-' * 50}")
        print("  [OK] Task addition test completed")

    except Exception as e:
        print(f"  [FAILED] Error adding task: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 5: Test planning
    print("\n[Step 5] Testing: Plan my day...")
    print("  User Input: 'Plan my day'")

    try:
        response = chat_handler.process_message("Plan my day")
        print(f"\n  Agent Response:\n  {'-' * 50}")
        for line in response.split("\n"):
            print(f"  {line}")
        print(f"  {'-' * 50}")
        print("  [OK] Planning test completed")

    except Exception as e:
        print(f"  [FAILED] Error planning day: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 6: Test suggestion agent
    print("\n[Step 6] Testing: What should I work on now?...")
    print("  User Input: 'What should I work on right now?'")

    try:
        response = chat_handler.process_message("What should I work on right now?")
        print(f"\n  Agent Response:\n  {'-' * 50}")
        for line in response.split("\n"):
            print(f"  {line}")
        print(f"  {'-' * 50}")
        print("  [OK] Suggestion test completed")

    except Exception as e:
        print(f"  [FAILED] Error getting suggestion: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 7: Verify task was created
    print("\n[Step 7] Verifying task was created in database...")

    try:
        tasks = task_service.list_tasks()
        print(f"  Found {len(tasks)} task(s) in database")
        for task in tasks[-3:]:  # Show last 3 tasks
            print(f"    - {task.title} (Priority: {task.priority}, Status: {task.status})")
        print("  [OK] Database verification completed")

    except Exception as e:
        print(f"  [FAILED] Error listing tasks: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("UAT TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return True


def test_direct_llm():
    """Test direct LLM service to verify connection."""
    print("\n" + "=" * 60)
    print("LLM CONNECTION TEST")
    print("=" * 60)

    try:
        from adhd_planner.services.llm_service import LLMService
        from adhd_planner.utils.config import get_settings

        settings = get_settings()
        print(f"\n[Config] LLM Provider: {settings.llm_provider}")

        if settings.llm_provider == "ollama":
            print(f"[Config] Ollama URL: {settings.ollama_base_url}")
            print(f"[Config] Ollama Model: {settings.ollama_model}")
        elif settings.llm_provider == "gemini":
            print(f"[Config] Gemini Model: {settings.gemini_model}")

        print("\n[Test] Initializing LLM Service...")
        llm_service = LLMService()

        print("[Test] Sending test prompt...")
        response = llm_service.generate(
            prompt="Say 'Hello, I am working!' in exactly 5 words.",
            system_prompt="You are a helpful assistant. Respond concisely.",
        )

        print(f"[Response] {response}")
        print("\n[OK] LLM connection successful!")
        return True

    except Exception as e:
        print(f"\n[FAILED] LLM connection error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    import os

    os.chdir(Path(__file__).parent.parent.parent)

    print(f"Working directory: {os.getcwd()}")

    # First test LLM connection
    llm_ok = test_direct_llm()

    if llm_ok:
        # Then test full workflow
        test_supervisor_and_agents()
    else:
        print("\n[SKIP] Skipping agent tests due to LLM connection failure")
        print("Please ensure your LLM provider is configured correctly in .env")
