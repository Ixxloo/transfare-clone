import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Transfer, TransferFile
from .storage import build_key, presigned_put, get_object_size, MAX_TRANSFER_BYTES


@require_POST
def upload_init(request):
    data = json.loads(request.body)
    files = data.get("files", [])

    if not files:
        return JsonResponse({"error": "No files."}, status=400)

    claimed_total = sum(int(f.get("size", 0)) for f in files)
    if claimed_total > MAX_TRANSFER_BYTES:
        return JsonResponse({"error": "Transfer exceeds 200 MB."}, status=413)

    transfer = Transfer.objects.create(
        owner=request.user if request.user.is_authenticated else None,
        message=data.get("message", ""),
    )

    uploads = []
    for f in files:
        key = build_key(transfer.id, f["name"])
        tf = TransferFile.objects.create(
            transfer=transfer,
            key=key,
            original_name=f["name"],
            content_type=f.get("type", "application/octet-stream"),
        )
        uploads.append({
            "file_id": tf.id,
            "name": tf.original_name,
            "url": presigned_put(key, tf.content_type),
        })

    return JsonResponse({"token": transfer.token, "uploads": uploads})


@require_POST
def upload_complete(request):
    data = json.loads(request.body)
    transfer = Transfer.objects.filter(token=data.get("token")).first()

    if not transfer:
        return JsonResponse({"error": "Not found."}, status=404)

    total = 0
    for tf in transfer.files.all():
        try:
            tf.size = get_object_size(tf.key)   # real size from R2
        except Exception:
            return JsonResponse({"error": f"Missing: {tf.original_name}"}, status=400)
        tf.uploaded = True
        tf.save()
        total += tf.size

    if total > MAX_TRANSFER_BYTES:
        transfer.delete()
        return JsonResponse({"error": "Transfer exceeds 200 MB."}, status=413)

    transfer.total_size = total
    transfer.is_complete = True
    transfer.save()

    return JsonResponse({"token": transfer.token, "download_url": f"/d/{transfer.token}/"})