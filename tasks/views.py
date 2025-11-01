from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.decorators import login_required
import uuid
from django.utils import timezone
from tasks.models import Task
# from login.models import Users
from django.contrib.auth.models import User
from datetime import timedelta

User = get_user_model()

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def tasks_api(request):
    # Get Supabase user
    # try:
    #     supabase_user = Users.objects.get(email=request.user.email)
    # except Users.DoesNotExist:
    #     return JsonResponse({"error": "Supabase user not found"}, status=404)
    local_user = User.objects.get(username=request.user.username)
    tasks = Task.objects.filter(user=local_user)

    #fetch tasks
    if request.method == "GET":
        year = request.GET.get('year')
        month = request.GET.get('month')
        # tasks = Task.objects.filter(user=supabase_user)

        if year and month:
            try:
                y = int(year)
                m = int(month) + 1
                tasks = tasks.filter(date__year=y, date__month=m)
            except ValueError:
                pass

        data = list(tasks.values())
        return JsonResponse({"tasks": data})

    # create new task/
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
        # user=supabase_user,
        user=local_user,
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

@login_required(login_url='login')
@require_http_methods(["GET", "PATCH", "DELETE"])
def task_detail_api(request, task_id: str):
    # Get Supabase user
    # try:
    #     supabase_user = Users.objects.get(email=request.user.email)
    # except Users.DoesNotExist:
    #     return JsonResponse({"error": "Supabase user not found"}, status=404)
    local_user = User.objects.get(username=request.user.username)
    task = Task.objects.filter(user=local_user, task_id=task_id).first()
    if not task:
        return JsonResponse({"error": "Task not found"}, status=404)

    # GET task details
    if request.method == "GET":
        return JsonResponse({
            "task": {
                "id": str(task.task_id),
                "task_name": task.task_name,
                "priority": task.priority,
                "status": task.status,
                "date": str(task.date),
                "hour": task.hour,
                "color": task.color,
                "description": task.description,
            }
        })

    # update task
    elif request.method == "PATCH":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")

        updated = False
        for field in ["task_name", "description", "date", "hour", "color", "priority", "status"]:
            if field in payload and payload[field] is not None:
                setattr(task, field, payload[field])
                updated = True

        if not updated:
            return JsonResponse({"error": "No fields to update"}, status=400)

        task.save()
        return JsonResponse({
            "task": {
                "id": str(task.task_id),
                "task_name": task.task_name,
                "priority": task.priority,
                "status": task.status,
                "date": str(task.date),
                "hour": task.hour,
                "color": task.color,
                "description": task.description,
            }
        })

    # DELETE task
    elif request.method == "DELETE":
        task.delete()
        return JsonResponse({"ok": True})


@login_required(login_url='login')
@require_http_methods(["GET"])
def weekly_summary_api(request):
    # try:
    #     supabase_user = Users.objects.get(email=request.user.email)
    # except Users.DoesNotExist:
    #     return JsonResponse({"error": "Supabase user not found"}, status=404)
    local_user = User.objects.get(username=request.user.username)

    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday

    # qs = Task.objects.filter(user=supabase_user, date__gte=start, date__lte=end)
    qs = Task.objects.filter(user=local_user, date__gte=start, date__lte=end)
    total = qs.count()
    completed = qs.filter(status__iexact="Completed").count()
    pending = qs.exclude(status__iexact="Completed").count()

    return JsonResponse({
        "start": str(start),
        "end": str(end),
        "total": total,
        "completed": completed,
        "pending": pending,
    })

@login_required(login_url='login')
@require_http_methods(["GET"])
def weekly_completion_stats_api(request):
    local_user = User.objects.get(username=request.user.username)

    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday

    tasks = Task.objects.filter(user=local_user, date__gte=start, date__lte=end)

    total = tasks.count()
    completed = tasks.filter(status__iexact="Completed").count()
    overdue = tasks.filter(date__lt=today).exclude(status__iexact="Completed").count()
    unfinished = total - completed - overdue

    completion_percentage = 0
    if total > 0:
        completion_percentage = round((completed / total) * 100, 2)

    return JsonResponse({
        "start": str(start),
        "end": str(end),
        "total_tasks": total,
        "completed_count": completed,
        "unfinished_count": unfinished,
        "overdue_count": overdue,
        "completion_percentage": completion_percentage,
    })

# @login_required(login_url='login')
# @require_http_methods(["GET", "POST"])
# def tasks_api(request):
#     user = request.user

#     if request.method == "GET":
#         year = request.GET.get('year')
#         month = request.GET.get('month')
#         tasks = Task.objects.filter(user=user)

#         if year and month:
#             try:
#                 y = int(year)
#                 m = int(month) + 1
#                 tasks = tasks.filter(date__year=y, date__month=m)
#             except ValueError:
#                 pass

#         data = list(tasks.values())
#         return JsonResponse({"tasks": data})

#     # POST
#     try:
#         payload = json.loads(request.body.decode("utf-8"))
#     except Exception:
#         return HttpResponseBadRequest("Invalid JSON")

#     title = payload.get("title")
#     date = payload.get("date")
#     hour = payload.get("hour")
#     color = payload.get("color") or "Green"
#     description = payload.get("description") or ""
#     priority = payload.get("priority") or "Medium"
#     status_val = payload.get("status") or "Pending"

#     if not title:
#         return JsonResponse({"error": "Title is required"}, status=400)
#     if not date:
#         return JsonResponse({"error": "Date is required"}, status=400)

#     task = Task.objects.create(
#         user=user,
#         task_name=title,
#         description=description,
#         date=date,
#         hour=hour,
#         color=color,
#         priority=priority,
#         status=status_val,
#     )

#     return JsonResponse({"task": {
#         "id": str(task.task_id),
#         "task_name": task.task_name,
#         "priority": task.priority,
#         "status": task.status,
#         "date": str(task.date),
#         "hour": task.hour,
#         "color": task.color,
#     }})

# @login_required(login_url='login')
# @require_http_methods(["GET", "PATCH", "DELETE"])
# def task_detail_api(request, task_id: str):
#     supabase_user = Users.objects.get(user_id=request.user.supabase_user_id)

#     try:
#         task = Task.objects.get(task_id=task_id, user=user)
#     except Task.DoesNotExist:
#         return JsonResponse({"error": "Not found"}, status=404)

#     if request.method == "GET":
#         return JsonResponse({
#             "task": {
#                 "id": str(task.task_id),
#                 "task_name": task.task_name,
#                 "priority": task.priority,
#                 "status": task.status,
#                 "date": str(task.date),
#                 "hour": task.hour,
#                 "color": task.color,
#                 "description": task.description,
#             }
#         })

#     elif request.method == "PATCH":
#         try:
#             payload = json.loads(request.body.decode("utf-8"))
#         except Exception:
#             return HttpResponseBadRequest("Invalid JSON")

#         updated = False
#         for field in ["task_name", "description", "date", "hour", "color", "priority", "status"]:
#             if field in payload and payload[field] is not None:
#                 setattr(task, field, payload[field])
#                 updated = True

#         if not updated:
#             return JsonResponse({"error": "No fields to update"}, status=400)

#         task.save()
#         return JsonResponse({
#             "task": {
#                 "id": str(task.task_id),
#                 "task_name": task.task_name,
#                 "priority": task.priority,
#                 "status": task.status,
#                 "date": str(task.date),
#                 "hour": task.hour,
#                 "color": task.color,
#                 "description": task.description,
#             }
#         })

#     elif request.method == "DELETE":
#         task.delete()
#         return JsonResponse({"ok": True})


# @login_required(login_url='login')
# @require_http_methods(["GET"])
# def weekly_summary_api(request):
#     user = request.user
#     today = timezone.localdate()
#     start = today - timedelta(days=today.weekday())  # Monday
#     end = start + timedelta(days=6)  # Sunday

#     qs = Task.objects.filter(user=user, date__gte=start, date__lte=end)
#     total = qs.count()
#     completed = qs.filter(status__iexact="Completed").count()
#     pending = qs.exclude(status__iexact="Completed").count()

#     return JsonResponse({
#         "start": str(start),
#         "end": str(end),
#         "total": total,
#         "completed": completed,
#         "pending": pending,
#     })


