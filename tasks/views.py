from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.decorators import login_required
import uuid
from django.utils import timezone
from tasks.models import Task

User = get_user_model()
@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def tasks_api(request):
    user = request.user

    if request.method == "GET":
        year = request.GET.get('year')
        month = request.GET.get('month')
        tasks = Task.objects.filter(user=user)

        if year and month:
            try:
                y = int(year)
                m = int(month) + 1
                tasks = tasks.filter(date__year=y, date__month=m)
            except ValueError:
                pass

        data = list(tasks.values())
        return JsonResponse({"tasks": data})

    # POST
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    title = payload.get("title")
    date = payload.get("date")
    hour = payload.get("hour")
    color = payload.get("color") or "Green"
    description = payload.get("description") or ""
    priority = payload.get("priority") or "Medium"
    status_val = payload.get("status") or "Pending"

    if not title:
        return JsonResponse({"error": "Title is required"}, status=400)
    if not date:
        return JsonResponse({"error": "Date is required"}, status=400)

    task = Task.objects.create(
        user=user,
        task_name=title,
        description=description,
        date=date,
        hour=hour,
        color=color,
        priority=priority,
        status=status_val,
    )

    return JsonResponse({"task": {
        "id": str(task.task_id),
        "task_name": task.task_name,
        "priority": task.priority,
        "status": task.status,
        "date": str(task.date),
        "hour": task.hour,
        "color": task.color,
    }})


# @login_required(login_url='login')
# @require_http_methods(["GET", "POST"])
# def tasks_api(request):
#     """
#     GET: return list of tasks for the logged-in user, optionally filtered by year & month.
#     POST: create a new task for the logged-in user.
#     """
#     user_id = request.session.get('user_id') or str(request.user.id)
#     print(f"DEBUG: tasks_api user_id from session: {user_id}")
#     if not user_id:
#         return JsonResponse({"error": "Not authenticated"}, status=401)

#     if request.method == "GET":
#         year = request.GET.get('year')
#         month = request.GET.get('month')  # 0-based from JS
#         query = supabase.table("task").select("*").eq("user_id", user_id)
#         if year is not None and month is not None:
#             try:
#                 y = int(year)
#                 m = int(month) + 1
#                 start = f"{y}-{m:02d}-01"
#                 if m == 12:
#                     end = f"{y+1}-01-01"
#                 else:
#                     end = f"{y}-{m+1:02d}-01"
#                 query = query.gte("date", start).lt("date", end)
#             except ValueError:
#                 pass
#         response = query.order("date").order("hour").execute()
#         return JsonResponse({"tasks": response.data or []})

#     try:
#         payload = json.loads(request.body.decode("utf-8"))
#     except Exception:
#         return HttpResponseBadRequest("Invalid JSON")

#     title = (payload.get("title") or "").strip()
#     date = payload.get("date")
#     hour = payload.get("hour")
#     color = payload.get("color") or "#2e7d32"
#     description = payload.get("description") or ""
#     priority = payload.get("priority") or None
#     status_val = payload.get("status") or "pending"

#     if not title:
#         return JsonResponse({"error": "Title is required"}, status=400)
#     if not date:
#         return JsonResponse({"error": "Date is required"}, status=400)
#     if hour is None or str(hour) == "":
#         return JsonResponse({"error": "Hour is required"}, status=400)

#     task_id = str(uuid.uuid4())
#     insert_data = {
#         "id": task_id,
#         "user_id": user_id,
#         "title": title,
#         "description": description,
#         "date": date,
#         "hour": int(hour),
#         "color": color,
#         "priority": priority,
#         "status": status_val,
#     }
#     resp = supabase.table("task").insert(insert_data).execute()
#     if not resp.data:
#         return JsonResponse({"error": "Failed to create task"}, status=500)
#     return JsonResponse({"task": resp.data[0]})


# @login_required(login_url='login')
# @require_http_methods(["GET", "PATCH", "DELETE"])
# def task_detail_api(request, task_id: str):
#     user_id = request.session.get('user_id') or str(request.user.id)
#     if not user_id:
#         return JsonResponse({"error": "Not authenticated"}, status=401)

#     # Ensure the task belongs to the user
#     if request.method == "GET":
#         resp = supabase.table("task").select("*").eq("id", task_id).eq("user_id", user_id).single().execute()
#         if not resp.data:
#             return JsonResponse({"error": "Not found"}, status=404)
#         return JsonResponse({"task": resp.data})

#     if request.method == "PATCH":
#         try:
#             payload = json.loads(request.body.decode("utf-8"))
#         except Exception:
#             return HttpResponseBadRequest("Invalid JSON")
#         update_fields = {}
#         for key in ["title", "description", "date", "hour", "color", "priority", "status"]:
#             if key in payload and payload[key] is not None:
#                 update_fields[key] = payload[key]
#         if not update_fields:
#             return JsonResponse({"error": "No fields to update"}, status=400)
#         resp = supabase.table("task").update(update_fields).eq("id", task_id).eq("user_id", user_id).execute()
#         if not resp.data:
#             return JsonResponse({"error": "Update failed"}, status=500)
#         return JsonResponse({"task": resp.data[0]})

#     # DELETE
#     resp = supabase.table("task").delete().eq("id", task_id).eq("user_id", user_id).execute()
#     return JsonResponse({"ok": True})