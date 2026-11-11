"""Hosted premium upscaling through Replicate Topaz API. Stdlib only (Python 3.8+).

Photos leave the machine only after explicit opt-in through the desktop UI.
Credentials are held in memory only and never written to disk.
"""
import io, json, time, uuid, urllib.request, urllib.error
from PIL import Image

API = "https://api.replicate.com/v1"
MODEL = API + "/models/topazlabs/image-upscale/predictions"

def _request(url, token, body=None, content_type="application/json", method=None, timeout=120):
    headers={"Authorization":"Bearer "+token,"Accept":"application/json"}
    if body is not None:
        headers["Content-Type"]=content_type
    req=urllib.request.Request(url, data=body, headers=headers, method=method or ("POST" if body is not None else "GET"))
    try:
        with urllib.request.urlopen(req,timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        msg=err.read().decode("utf-8","replace")[:1300]
        raise RuntimeError("Premium service HTTP {}: {}".format(err.code,msg))

def _upload(image, token):
    buffer=io.BytesIO()
    image.convert("RGB").save(buffer,format="JPEG",quality=94,subsampling=0)
    raw=buffer.getvalue()
    boundary="----ImageRestoreStudio"+uuid.uuid4().hex
    head=("--"+boundary+'\r\nContent-Disposition: form-data; name="content"; filename="photo.jpg"\r\nContent-Type: image/jpeg\r\n\r\n').encode("utf-8")
    body=head+raw+('\r\n--'+boundary+'--\r\n').encode("utf-8")
    result=_request(API+"/files", token,body,
        "multipart/form-data; boundary="+boundary, timeout=180)
    url=result.get("urls",{}).get("get")
    if not url:
        raise RuntimeError("Provider did not return an uploaded image URL.")
    return url

def upscale(image, factor, token, profile="Low Resolution V2", face=True):
    if factor not in (2,4,6):
        raise ValueError("Topaz Premium supports 2×, 4× or 6×, not {}×. Please select a supported scale.".format(factor))
    if not token or not token.strip():
        raise RuntimeError("Add a Replicate API token using 'Premium account' first.")
    uploaded=_upload(image,token.strip())
    request_input={
        "image":uploaded,"enhance_model":profile,
        "upscale_factor":str(factor)+"x","output_format":"png",
        "face_enhancement":bool(face),
        "face_enhancement_creativity":0.0,
        "face_enhancement_strength":0.65,
    }
    payload=json.dumps({"input":request_input}).encode("utf-8")
    task=_request(MODEL,token.strip(),payload,timeout=120)
    for i in range(120):
        status=task.get("status")
        if status=="succeeded":break
        if status in ("failed","canceled"):
            raise RuntimeError("Premium processing "+status+": "+str(task.get("error") or "Unknown error"))
        time.sleep(3)
        task_id=task.get("id")
        if not task_id:raise RuntimeError("Missing prediction ID from premium service.")
        task=_request(API+"/predictions/"+task_id,token.strip(),timeout=60)
    else:
        raise RuntimeError("Premium processing exceeded six minutes. Check Replicate predictions before retrying: the first request may still incur charges.")
    output=task.get("output")
    if isinstance(output,list):
        output=next((x for x in output if isinstance(x,str)),None)
    if not isinstance(output,str) or not output.startswith("https://"):
        raise RuntimeError("No output image URL returned by premium service.")
    with urllib.request.urlopen(urllib.request.Request(output,headers={"User-Agent":"ImageRestoreStudio/0.5"}),timeout=120) as response:
        data=response.read(250*1024*1024+1)
    if len(data)>250*1024*1024:
        raise RuntimeError("Premium output image exceeds safety size limit.")
    with Image.open(io.BytesIO(data)) as output_image:
        result=output_image.convert("RGB")
    expected=(image.width*factor,image.height*factor)
    if result.size!=expected:
        raise RuntimeError("Premium provider returned {} rather than expected {}. Image not resized artificially.".format(result.size,expected))
    return result
