from app import app


@app.route('/scale/web')
def scale_check_web():
    scale_check_web.ncalls += 1
    if scale_check_web.ncalls % 5 == 0:
        return 'UP', 503

    return 'OK', 200
scale_check_web.ncalls = 0


@app.route('/scale/worker')
def scale_check_worker():
    scale_check_worker.ncalls += 1
    if scale_check_worker.ncalls % 10 == 0:
        return 'UP', 503

    return 'OK', 200
scale_check_worker.ncalls = 0
