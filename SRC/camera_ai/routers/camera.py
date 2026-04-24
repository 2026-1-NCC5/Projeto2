from fastapi import APIRouter
import camera_process as cam

router = APIRouter(prefix="/camera")


@router.get("/status")
def status():
    return {"running": cam.is_running()}


@router.post("/start")
def start():
    return cam.start()


@router.post("/stop")
def stop():
    return cam.stop()


@router.post("/finish")
def finish():
    return cam.finish()
