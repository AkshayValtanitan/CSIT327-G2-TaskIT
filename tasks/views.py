from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
import uuid
from django.utils import timezone
from datetime import timedelta
from taskit_project.supabase_client import supabase
from calendar import monthrange
from datetime import datetime, date, timedelta, time

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def tasks_api(request):
    user_id = request.session.get("supabase_user_id")
    print("User ID in session:", user_id)
    if not user_id:
        return JsonResponse({"error": "Supabase user_id not found"}, status=400)

    if request.method == "GET":
        year = request.GET.get("year")
        month = request.GET.get("month")

        try:
            y = int(year)
            m = int(month)
        except (TypeError, ValueError):
            return JsonResponse({"error": "Invalid year or month"}, status=400)

        # now safe to get last day
        last_day = monthrange(y, m)[1]
        start_date = f"{y}-{m:02d}-01"
        end_date = f"{y}-{m:02d}-{last_day:02d}"

        query = supabase.table("task").select("*").eq("user_id", user_id)
        query = query.gte("date", start_date).lte("date", end_date)

        data = query.execute()
        return JsonResponse({"tasks": data.data if data.data else []})  # changed key to "tasks" to match frontend

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    required_fields = ["title", "date"]
    for field in required_fields:
        if not payload.get(field):
            return JsonResponse({"error": f"{field} is required"}, status=400)

    task_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": payload.get("title"),
        "description": payload.get("description") or "",
        "date": payload.get("date"),
        "hour": payload.get("hour") or "",
        "color": payload.get("color") or "Green",
        "priority": payload.get("priority") or "Medium",
        "status": payload.get("status") or "Pending",
        "date_created": timezone.now().isoformat(),
        "date_updated": timezone.now().isoformat(),
    }

    response = supabase.table("task").insert(task_data).execute()
    # return JsonResponse({"tasks": response.data[0] if response.data else task_data})
    return JsonResponse({"tasks": [response.data[0]] if response.data else [task_data]})


@login_required(login_url='login')
@require_http_methods(["GET", "PATCH", "DELETE"])
def task_detail_api(request, task_id):
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return JsonResponse({"error": "Supabase user_id not found"}, status=400)

    task_res = supabase.table("task").select("*").eq("id", task_id).eq("user_id", user_id).execute()
    if not task_res.data:
        return JsonResponse({"error": "Task not found"}, status=404)
    task = task_res.data[0]

    if request.method == "GET":
        return JsonResponse({"tasks": task})

    elif request.method == "PATCH":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")

        update_data = {k: v for k, v in payload.items() if k in ["title", "description", "date", "hour", "color", "priority", "status"]}
        if not update_data:
            return JsonResponse({"error": "No fields to update"}, status=400)

        update_data["date_updated"] = timezone.now().isoformat()
        updated = supabase.table("task").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
        return JsonResponse({"tasks": updated.data[0] if updated.data else task})

    elif request.method == "DELETE":
        supabase.table("task").delete().eq("id", task_id).eq("user_id", user_id).execute()
        return JsonResponse({"ok": True})


@login_required(login_url='login')
@require_http_methods(["GET"])
def weekly_summary_api(request):
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return JsonResponse({"error": "Supabase user_id not found"}, status=400)
    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    start_dt = datetime.combine(start, time.min)
    end_dt = datetime.combine(end, time.max)

    # tasks_res = supabase.table("task").select("*").eq("user_id", user_id).gte("date", str(start_dt)).lte("date", str(end_dt)).execute()
    tasks_res = supabase.table("task").select("*")\
        .eq("user_id", user_id)\
        .gte("date", start_dt.isoformat())\
        .lte("date", end_dt.isoformat())\
        .execute()
    tasks = tasks_res.data or []

    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("status", "").lower() == "completed")
    pending = total - completed

    WARNING_THRESHOLD = 5 
    overload_warning = total > WARNING_THRESHOLD

    return JsonResponse({
        "start": str(start),
        "end": str(end),
        "total": total,
        "completed": completed,
        "pending": pending,
        "overload_warning": overload_warning,
    })


@login_required(login_url='login')
@require_http_methods(["GET"])
def weekly_completion_stats_api(request):
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return JsonResponse({"error": "Supabase user_id not found"}, status=400)

    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    # Convert dates to ISO format (YYYY-MM-DD) for Supabase
    start_iso = start.isoformat()
    end_iso = end.isoformat()

    # Fetch tasks only for this user and this week
    # tasks_res = supabase.table("task").select("*")\
    #     .eq("user_id", user_id)\
    #     .gte("date", start_iso)\
    #     .lte("date", end_iso)\
    #     .execute()
    
    tasks_res = supabase.table("task").select("*")\
        .eq("user_id", user_id)\
        .execute()

    tasks = tasks_res.data or []

    print("DEBUG: total tasks fetched for user:", len(tasks))
    for t in tasks:
        print("DEBUG TASK:", t.get("date"), t.get("status"))
    
    tasks = tasks_res.data or []

    total = len(tasks)
    completed = overdue = unfinished = 0

    for t in tasks:
        status = (t.get("status") or "").strip().lower()
        date_str = t.get("date")
        if not date_str:
            continue

        # Extract date part only
        task_date = date_str[:10]  # 'YYYY-MM-DD'
        task_date = datetime.strptime(task_date, "%Y-%m-%d").date()

        if status == "completed":
            completed += 1
        elif task_date < today:
            overdue += 1
        else:
            unfinished += 1

    completion_percentage = round((completed / total) * 100, 2) if total else 0

    return JsonResponse({
        "start": str(start),
        "end": str(end),
        "total_tasks": total,
        "completed_count": completed,
        "unfinished_count": unfinished,
        "overdue_count": overdue,
        "completion_percentage": completion_percentage,
    })
