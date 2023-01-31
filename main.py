import uvicorn
import fastapi as _fastapi
from fastapi import Request, Form, UploadFile, File, HTTPException
import blockchain as _blockchain
import zkproof as _zkproof
import json
import os
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

blockchain = _blockchain.Blockchain()
zkproof = _zkproof
app = _fastapi.FastAPI()
     
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    _zkproof.zkproofstartup()
    
if __name__ == '__main__':
    uvicorn.run(app)

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    if (electioncurrent()==True):
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return templates.TemplateResponse("index-no-election.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
def return_form(request: Request, zkproof : str = Form(...)):

    status = validate(request,zkproof)
    if (status == True):
        return RedirectResponse(url=f"/vote/", status_code=303)
    else:
        return templates.TemplateResponse("index-fail.html", {"request": request})

@app.get("/registration", response_class=HTMLResponse)
def registrationpage(request: Request):
    if (electioncurrent()==True):
        return templates.TemplateResponse("registration.html", {"request": request})
    else:
        return templates.TemplateResponse("index-no-election.html", {"request": request})

@app.post("/registration", response_class=HTMLResponse)
def return_form(request: Request, name: str = Form(...), age: int = Form(...), faculty : str = Form(...), email : str = Form(...), studentid : str = Form(...)):

    userdata = name + ":" + str(age) + ":" + faculty + ":" + email + ":" + studentid
    _zkproof.clientobtainrestart()
    print(userdata)
    return get_zkproofstatement(request, userdata)

@app.get("/vote", response_class=HTMLResponse)
def vote_page(request: Request):
    if (electioncurrent()==True):
        candidate_a_data = getdata(candidate_a)
        name = candidate_a_data[0]
        year = candidate_a_data[1]
        faculty = candidate_a_data[2]
        slogan = candidate_a_data[3]
        
        candidate_b_data = getdata(candidate_b)
        name2 = candidate_b_data[0]
        year2 = candidate_b_data[1]
        faculty2 = candidate_b_data[2]
        slogan2 = candidate_b_data[3]
        
        return templates.TemplateResponse("vote.html", {"request": request, "name" : name, "year" : year, "faculty" : faculty, "slogan" : slogan, "name2" : name2, "year2" : year2, "faculty2" : faculty2, "slogan2" : slogan2})
    else:
        return templates.TemplateResponse("index-no-election.html", {"request": request})

@app.post("/vote", response_class=HTMLResponse)
def votecandidate(request: Request, votesubmit : int = Form(...), zkproofagain : str = Form(...)):
    
    if (votesubmit == 1):
        votecountA = increment_A()
    elif (votesubmit == 2):
        votecountB = increment_B()
        
    votecountA = str(votecount_A)
    votecountB = str(votecount_B)
        
    transaction = str(zkproofagain) + ":" + "Election" + ":" + votecountA + ":" + votecountB
    print(transaction)
    
    return mine_block(request,transaction)

@app.get("/blockchain", response_class=HTMLResponse)
def blockchainpage(request: Request):
    if (electioncurrent()==False and checkchain() != 1):
        return templates.TemplateResponse("blockchain.html", {"request": request})
    elif(electioncurrent()==True):
        return templates.TemplateResponse("blockchain-nosee.html", {"request": request})
    else:
        return templates.TemplateResponse("index-no-election.html", {"request": request})

@app.post("/blockchain",response_class=HTMLResponse)
def blockchainfind(request: Request, zkproof : str = Form(...)):
    return find_transaction(request, zkproof)

@app.get("/results", response_class=HTMLResponse)
def get_results(request: Request):
    if (electioncurrent()==False and checkchain() != 1):
    
        prev_block = blockchain._get_prev_block()
        transaction = prev_block["transaction"]
        str(transaction)
        print(transaction)
        votecount_B = transaction.rsplit(":")[-1]
        print(votecount_B)
        votecount_A = transaction.rsplit(":")[-2]
        print(votecount_A)
        
        candidate_a_data = getdata(candidate_a)
        name = candidate_a_data[0]
        candidate_b_data = getdata(candidate_b)
        name2 = candidate_b_data[0]

        return templates.TemplateResponse("results.html", {"request": request,"votecountA" : votecount_A, "votecountB" : votecount_B, "name" : name, "name2" : name2})
    
    elif(electioncurrent()==True):
        return templates.TemplateResponse("results-nosee.html", {"request": request})
    
    else:
        return templates.TemplateResponse("index-no-election.html", {"request": request})

@app.get("/downloadchain", response_class=FileResponse)
def downloadchain(request: Request):
    with open('electiondata.txt','w') as convert_file:
        convert_file.write(json.dumps(blockchain.chain, indent=4, sort_keys=True))
    
    filepath = "electiondata.txt"
    
    return FileResponse(path = filepath, filename= filepath, media_type = 'text')

@app.get("/registration-done")
def home(request: Request):
    return templates.TemplateResponse("registration-done.html", {"request": request})

@app.get("/index-fail")
def home(request: Request):
    return templates.TemplateResponse("index-fail.html", {"request": request})

#Admin

@app.get("/admin", response_class=HTMLResponse)
def adminlogin(request: Request):
        return templates.TemplateResponse("admin-login.html", {"request": request})
    
@app.post("/admin", response_class=HTMLResponse)
def adminlogin(request: Request, username : str = Form(...), password : str = Form(...)):
    if (username == "admin" and password == "blockchain"):
        return RedirectResponse(url=f"/adminpanel", status_code=303)
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
@app.get("/adminpanel", response_class=HTMLResponse)
def adminpanel(request: Request):
        return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/adminpanel", response_class=HTMLResponse)
def adminaction(request: Request, buttondata : str = Form(...)):
    if (buttondata == "Start Election"):
        electionstart()
        return templates.TemplateResponse("admin-start.html", {"request": request})
    elif (buttondata == "End Election"):
        electionend()
        return templates.TemplateResponse("admin-end.html", {"request": request})
    elif (buttondata == "Modify Candidates"):
        return RedirectResponse(url=f"/modifycandidate", status_code=303)
    elif (buttondata == "Blockchain Validity"):
        validity = blockchain._chain_validity()
        return templates.TemplateResponse("admin-chainvalidity.html", {"request": request,"validity" : validity})
    
@app.get("/modifycandidate", response_class=HTMLResponse)
def modifycandidate(request: Request):
        return templates.TemplateResponse("admin-modify-candidate.html", {"request": request})
    
@app.post("/modifycandidate", response_class=HTMLResponse)
async def addcandidate(request: Request, a_pic : UploadFile = File(...), name : str = Form(...), year : str = Form(...), faculty : str = Form(...), slogan : str = Form(...), b_pic : UploadFile = File(...), name2 : str = Form(...), year2 : str = Form(...), faculty2 : str = Form(...), slogan2 : str = Form(...)):
    
    candidate_a = await a_pic.read()
    a_filetype =  (a_pic.filename.rsplit(".")[-1])
    a_pic.filename = f"candidate_a.{a_filetype}"
    candidate_a_write = f"static/assets/{a_pic.filename}"
    open(candidate_a_write, "wb").write(candidate_a)
    
    if (a_filetype != "png"):
        image = Image.open(candidate_a_write)
        image.save(f"static/assets/candidate_a.png")
        os.remove(candidate_a_write)
    
    addcandidate_a(name, year, faculty, slogan)
    a_pic.file.close()
    
    candidate_b = await b_pic.read()
    b_filetype =  (b_pic.filename.rsplit(".")[-1])
    b_pic.filename = f"candidate_b.{b_filetype}"
    candidate_b_write = f"static/assets/{b_pic.filename}"
    open(candidate_b_write, "wb").write(candidate_b)
    
    if (b_filetype != "png"):
        image = Image.open(candidate_b_write)
        image.save(f"static/assets/candidate_b.png")
        os.remove(candidate_b_write)
    
    addcandidate_b(name2, year2, faculty2, slogan2)
    b_pic.file.close()
    
    return RedirectResponse(url=f"/adminpanel", status_code=303)

#Blockchain operations

@app.post("/mine_block/")
def mine_block(request : Request,transaction: str):
    if not blockchain._chain_validity():
        return _fastapi.HTTPException(status_code=400, detail="Chain invalid")

    block = blockchain._mine_block(transaction=transaction)
    
    return templates.TemplateResponse("vote-complete.html", {"request": request})

@app.get("/blockchain/")
def get_chain():
    if not blockchain._chain_validity():
        return _fastapi.HTTPException(status_code=400, detail="Chain invalid")
    
    with open('electiondata.txt','w') as convert_file:
        convert_file.write(json.dumps(blockchain.chain, indent=4, sort_keys=True))
    
    return blockchain.chain

@app.get("/validate/")
def chain_validity():
    if not blockchain._chain_validity():
        return _fastapi.HTTPException(status_code=400, detail="Chain invalid")

    return blockchain._chain_validity()

@app.get("/find_transaction/")
def find_transaction(request, zkproof: str):
    chain = blockchain._search_block(zkproof)
    
    index = chain[0]
    timestamp = chain[1]
    transaction = chain[2]
    nonce = chain[3]
    prev_hash = chain[4]

    return templates.TemplateResponse("blockchain-results.html", {"request": request, "index": index, "timestamp" : timestamp, "transaction": transaction, "nonce": nonce, "prev_hash" : prev_hash})

@app.get("/final_block/")
def final_block():
    if not blockchain._chain_validity():
        return _fastapi.HTTPException(status_code=400, detail="The blockchain is invalid")
        
    return blockchain._get_prev_block()

#ZK Proof Operations

@app.post("/get_zkproof/")
def get_zkproofstatement(request: Request, userdata):
    global zkproofstatement
    zkproofstatement = _zkproof.studentsignature(userdata)
    print(zkproofstatement)
    return get_zkproof(request, zkproofstatement)

@app.post("/get_token/")
def get_zkproof(request: Request,zkproofstatement: str):
    global tokencontent
    
    tokencontent = _zkproof.tokenpassing(zkproofstatement)
    print(tokencontent)
    
    return templates.TemplateResponse("registration-done.html", {"request": request, "zkproofstatement": zkproofstatement})

@app.post("/validate_zkproof")
def validate(request : Request, zkproof: str):
    token = tokencontent
    status = _zkproof.zkproofvalidate(token,zkproof)
    
    print(status)
    
    return status

def increment_A():
    global votecount_A
    votecount_A = votecount_A + 1
    
    return increment_A
    
def increment_B():
    global votecount_B
    votecount_B = votecount_B + 1
    
    return increment_B

def electionstart():
    global electionstatus
    electionstatus = True
    return electionstatus

def electionend():
    global electionstatus
    electionstatus = False
    return electionstatus

def electioncurrent():
    global electionstatus
    return electionstatus

def checkchain():
    prev_block = blockchain._get_prev_block()
    nonce = prev_block["nonce"]
    int(nonce)
    
    return nonce

def addcandidate_a(name: str, year: str, faculty: str, slogan: str) -> dict:
    global candidate_a
    name = str.upper(name)
    candidate_a = {
        "name" : name,
        "year" : year,
        "faculty" : faculty,
        "slogan" : slogan,
    }
    
    print(candidate_a)
    return candidate_a

def addcandidate_b(name2: str, year2: str, faculty2: str, slogan2: str) -> dict:
    
    global candidate_b
    name2 = str.upper(name2)
    candidate_b = {
        "name" : name2,
        "year" : year2,
        "faculty" : faculty2,
        "slogan" : slogan2,
    }
    
    print(candidate_b)
    return candidate_b

def getdata(candidate : dict) -> dict:
    result = candidate
    print(result)
    
    name = result.get('name')
    year = result.get('year')
    faculty = result.get('faculty')
    slogan = result.get('slogan')
    
    return (name, year, faculty, slogan)

#Global Variables

votecount_A = 0
votecount_B = 0
electionstatus = False