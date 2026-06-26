# main.py — EV Charge 2.0 | Backend completo con SQLite/PostgreSQL
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import hashlib, secrets
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import Optional, List
import requests
import uuid
import random
import os

# ─── Configuración ────────────────────────────────────────────────────────────

POSTGRES_USER = os.getenv("POSTGRES_USER", "evcharge_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "evcharge_pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "evcharge")

# DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
DATABASE_URL = "sqlite:///./ev_charge.db"

SECRET_KEY = "sena-ev-charge-secret-2024-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ─── Modelos de Base de Datos ─────────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuarios"
    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre        = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_admin      = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.now(timezone.utc))

    vehiculos     = relationship("Vehiculo", back_populates="usuario", cascade="all, delete-orphan")
    calificaciones= relationship("Calificacion", back_populates="usuario", cascade="all, delete-orphan")
    reportes      = relationship("Reporte", back_populates="usuario", cascade="all, delete-orphan")
    favoritos     = relationship("Favorito", back_populates="usuario", cascade="all, delete-orphan")
    reservas      = relationship("Reserva", back_populates="usuario", cascade="all, delete-orphan")
    metodos_pago  = relationship("MetodoPago", back_populates="usuario", cascade="all, delete-orphan")
    cargas        = relationship("Carga", back_populates="usuario", cascade="all, delete-orphan")

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id    = Column(String, ForeignKey("usuarios.id"), nullable=False)
    marca         = Column(String, nullable=False)
    modelo        = Column(String, nullable=False)
    anio          = Column(Integer)
    autonomia_km  = Column(Float, default=300)
    tipo_conector = Column(String, nullable=False)
    activo        = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.now(timezone.utc))

    usuario       = relationship("Usuario", back_populates="vehiculos")

class Calificacion(Base):
    __tablename__ = "calificaciones"
    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id     = Column(String, ForeignKey("usuarios.id"), nullable=False)
    estacion_ocm_id= Column(String, nullable=False, index=True)
    estacion_nombre= Column(String)
    puntaje        = Column(Integer, nullable=False)
    comentario     = Column(Text, default="")
    fecha          = Column(DateTime, default=datetime.now(timezone.utc))

    usuario        = relationship("Usuario", back_populates="calificaciones")

class Reporte(Base):
    __tablename__ = "reportes"
    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id     = Column(String, ForeignKey("usuarios.id"), nullable=False)
    estacion_ocm_id= Column(String, nullable=False, index=True)
    estacion_nombre= Column(String)
    tipo           = Column(String)
    descripcion    = Column(Text, default="")
    estado         = Column(String, default="abierto")
    fecha          = Column(DateTime, default=datetime.now(timezone.utc))

    usuario        = relationship("Usuario", back_populates="reportes")

class Favorito(Base):
    __tablename__ = "favoritos"
    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id     = Column(String, ForeignKey("usuarios.id"), nullable=False)
    estacion_ocm_id= Column(String, nullable=False)
    estacion_nombre= Column(String)
    fecha          = Column(DateTime, default=datetime.now(timezone.utc))

    usuario        = relationship("Usuario", back_populates="favoritos")

class Reserva(Base):
    __tablename__ = "reservas"
    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id       = Column(String, ForeignKey("usuarios.id"), nullable=False)
    estacion_ocm_id  = Column(String, nullable=False, index=True)
    estacion_nombre  = Column(String)
    fecha_hora_inicio= Column(DateTime, nullable=False)
    fecha_hora_fin   = Column(DateTime, nullable=False)
    estado           = Column(String, default="activa")
    created_at       = Column(DateTime, default=datetime.now(timezone.utc))

    usuario          = relationship("Usuario", back_populates="reservas")

class EstacionPropia(Base):
    __tablename__ = "estaciones_propias"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre      = Column(String, nullable=False)
    direccion   = Column(String)
    lat         = Column(Float, nullable=False)
    lon         = Column(Float, nullable=False)
    tipo_conector = Column(String)
    potencia_kw = Column(Float)
    descripcion = Column(String, default="")
    activa      = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.now(timezone.utc))

class MetodoPago(Base):
    __tablename__ = "metodos_pago"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id  = Column(String, ForeignKey("usuarios.id"), nullable=False)
    tipo        = Column(String, nullable=False)
    numero      = Column(String, nullable=False)
    estado      = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.now(timezone.utc))

    usuario     = relationship("Usuario", back_populates="metodos_pago")

class Carga(Base):
    __tablename__ = "cargas"
    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id     = Column(String, ForeignKey("usuarios.id"), nullable=False)
    estacion_ocm_id= Column(String, nullable=False)
    estacion_nombre= Column(String)
    kwh_cargados   = Column(Float, nullable=False)
    costo_estimado = Column(Float, nullable=False)
    notas          = Column(Text, default="")
    fecha          = Column(DateTime, default=datetime.now(timezone.utc))

    usuario        = relationship("Usuario", back_populates="cargas")


# ─── Crear tablas y Admin ─────────────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${h}"

def seed_admin(db: Session):
    try:
        admin = db.query(Usuario).filter(Usuario.email == "terpel@evcharge.co").first()
        if admin: return
        admin = Usuario(
            nombre="Terpel", 
            email="terpel@evcharge.co",
            password_hash=hash_password("123456"), 
            is_admin=True
        )
        db.add(admin); db.commit()
        print("✅ Admin Terpel creado con contraseña: 123456")
    except Exception as e:
        print(f"❌ Error creando admin: {e}")

with SessionLocal() as _db:
    seed_admin(_db)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        salt, h = hashed.split("$")
        return hashlib.sha256((salt + plain).encode()).hexdigest() == h
    except Exception:
        return False

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exc = HTTPException(status_code=401, detail="Token inválido o expirado")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id: raise credentials_exc
    except JWTError:
        raise credentials_exc
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user: raise credentials_exc
    return user

def require_admin(current_user: Usuario = Depends(get_current_user)):
    if not current_user.is_admin: raise HTTPException(status_code=403, detail="Acceso solo para administradores")
    return current_user

# ─── Schemas Pydantic ─────────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nombre: str; email: str; password: str

class UsuarioOut(BaseModel):
    id: str; nombre: str; email: str; is_admin: bool = False; created_at: datetime
    class Config: from_attributes = True

class TokenOut(BaseModel):
    access_token: str; token_type: str; usuario: UsuarioOut

class VehiculoCreate(BaseModel):
    marca: str; modelo: str; anio: Optional[int] = None
    autonomia_km: float = 300; tipo_conector: str; activo: bool = True
    class Config: from_attributes = True

class VehiculoUpdate(BaseModel):
    marca: Optional[str] = None; modelo: Optional[str] = None
    anio: Optional[int] = None; autonomia_km: Optional[float] = None
    tipo_conector: Optional[str] = None; activo: Optional[bool] = None
    class Config: from_attributes = True

class ReservaCreate(BaseModel):
    estacion_ocm_id: str; estacion_nombre: str = ""
    fecha_hora_inicio: datetime; fecha_hora_fin: datetime
    estado: str = "activa"
    class Config: from_attributes = True

class ReservaUpdate(BaseModel):
    estacion_ocm_id: Optional[str] = None; estacion_nombre: Optional[str] = None
    fecha_hora_inicio: Optional[datetime] = None; fecha_hora_fin: Optional[datetime] = None
    estado: Optional[str] = None
    class Config: from_attributes = True

class MetodoPagoCreate(BaseModel):
    tipo: str; numero: str; estado: bool = True
    class Config: from_attributes = True

class MetodoPagoUpdate(BaseModel):
    tipo: Optional[str] = None; numero: Optional[str] = None; estado: Optional[bool] = None
    class Config: from_attributes = True

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(title="EV Charge 2.0 — SENA")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

# ─── Rutas: Autenticación ─────────────────────────────────────────────────────

@app.post("/auth/registro", response_model=TokenOut)
def registro(data: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = Usuario(nombre=data.nombre, email=data.email, password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    token = create_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "usuario": user}

@app.post("/auth/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "usuario": user}

@app.get("/auth/perfil")
def perfil(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    db.refresh(current_user)
    vehiculo_activo = db.query(Vehiculo).filter(Vehiculo.usuario_id == current_user.id, Vehiculo.activo == True).first()
    return {"usuario": current_user, "vehiculo_activo": vehiculo_activo}

# ─── Rutas: Vehículos (usuario) ──────────────────────────────────────────────

@app.get("/vehiculos", response_model=List[VehiculoCreate])
def listar_vehiculos(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Vehiculo).filter(Vehiculo.usuario_id == current_user.id).all()

@app.post("/vehiculos")
def crear_vehiculo(data: VehiculoCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.activo:
        db.query(Vehiculo).filter(Vehiculo.usuario_id == current_user.id).update({"activo": False})
    v = Vehiculo(usuario_id=current_user.id, **data.model_dump())
    db.add(v); db.commit(); db.refresh(v)
    return v

@app.put("/vehiculos/{vid}/activar")
def activar_vehiculo(vid: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid, Vehiculo.usuario_id == current_user.id).first()
    if not v: raise HTTPException(404, "Vehículo no encontrado")
    db.query(Vehiculo).filter(Vehiculo.usuario_id == current_user.id).update({"activo": False})
    v.activo = True
    db.commit()
    return {"ok": True}

@app.delete("/vehiculos/{vid}")
def eliminar_vehiculo(vid: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid, Vehiculo.usuario_id == current_user.id).first()
    if not v: raise HTTPException(404, "Vehículo no encontrado")
    db.delete(v); db.commit()
    return {"ok": True}

# ─── Rutas: Reservas (usuario) ───────────────────────────────────────────────

@app.get("/mis-reservas")
def mis_reservas(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Reserva).filter(Reserva.usuario_id == current_user.id).order_by(Reserva.fecha_hora_inicio.asc()).all()

@app.post("/reservar")
def crear_reserva(data: ReservaCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.fecha_hora_inicio >= data.fecha_hora_fin: raise HTTPException(400, "Inicio debe ser anterior a Fin")
    if data.fecha_hora_inicio < datetime.now(timezone.utc): raise HTTPException(400, "No se puede reservar en el pasado")
    solapada = db.query(Reserva).filter(Reserva.estacion_ocm_id == data.estacion_ocm_id, Reserva.estado == "activa", Reserva.fecha_hora_inicio < data.fecha_hora_fin, Reserva.fecha_hora_fin > data.fecha_hora_inicio).first()
    if solapada: raise HTTPException(400, f"Estación reservada de {solapada.fecha_hora_inicio} a {solapada.fecha_hora_fin}")
    
    # CREAMOS LA RESERVA
    reserva = Reserva(usuario_id=current_user.id, **data.model_dump())
    db.add(reserva); db.commit(); db.refresh(reserva)

    # 🚀 AUTOMATIZACIÓN: Creamos la carga automáticamente asociada a esta reserva
    kwh_aleatorio = round(random.uniform(10.0, 30.0), 1)  # Entre 10 y 30 kWh
    costo_estimado = round(kwh_aleatorio * 1200, 0)       # 1200 COP por kWh simulado
    carga_automatica = Carga(
        usuario_id=current_user.id,
        estacion_ocm_id=data.estacion_ocm_id,
        estacion_nombre=data.estacion_nombre,
        kwh_cargados=kwh_aleatorio,
        costo_estimado=costo_estimado,
        notas=f"Carga automática generada por la reserva del {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}"
    )
    db.add(carga_automatica)
    db.commit()  # Guardamos la carga automática

    return reserva

@app.put("/reservas/{rid}")
def actualizar_reserva(rid: str, data: ReservaUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == rid, Reserva.usuario_id == current_user.id).first()
    if not reserva: raise HTTPException(404, "Reserva no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(reserva, key, value)
    db.commit(); db.refresh(reserva)
    return reserva

@app.patch("/reservas/{rid}/cancelar")
def cancelar_reserva(rid: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == rid, Reserva.usuario_id == current_user.id).first()
    if not reserva: raise HTTPException(404, "Reserva no encontrada")
    reserva.estado = "cancelada"; db.commit()
    return {"ok": True}

# ─── Rutas: Métodos de Pago (usuario) ─────────────────────────────────────────

@app.get("/pagos")
def listar_pagos(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(MetodoPago).filter(MetodoPago.usuario_id == current_user.id).all()

@app.post("/pagos")
def crear_pago(data: MetodoPagoCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    pago = MetodoPago(usuario_id=current_user.id, **data.model_dump())
    db.add(pago); db.commit(); db.refresh(pago)
    return pago

@app.put("/pagos/{pid}")
def actualizar_pago(pid: str, data: MetodoPagoUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    pago = db.query(MetodoPago).filter(MetodoPago.id == pid, MetodoPago.usuario_id == current_user.id).first()
    if not pago: raise HTTPException(404, "Método de pago no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(pago, key, value)
    db.commit(); db.refresh(pago)
    return pago

@app.delete("/pagos/{pid}")
def eliminar_pago(pid: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    pago = db.query(MetodoPago).filter(MetodoPago.id == pid, MetodoPago.usuario_id == current_user.id).first()
    if not pago: raise HTTPException(404, "Método de pago no encontrado")
    db.delete(pago); db.commit()
    return {"ok": True}

# ─── Rutas: Historial de Cargas ──────────────────────────────────────────────

@app.get("/cargas")
def listar_cargas(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Carga).filter(Carga.usuario_id == current_user.id).order_by(Carga.fecha.desc()).all()

@app.get("/cargas/estadisticas")
def estadisticas_cargas(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    cargas = db.query(Carga).filter(Carga.usuario_id == current_user.id).all()
    total_kwh = sum(c.kwh_cargados for c in cargas)
    total_costo = sum(c.costo_estimado for c in cargas)
    return {"total_sesiones": len(cargas), "total_kwh": round(total_kwh, 2), "total_costo": round(total_costo, 0)}

@app.post("/cargas")
def crear_carga(data: dict, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    carga = Carga(usuario_id=current_user.id, **data)
    db.add(carga); db.commit(); db.refresh(carga)
    return carga


# ─── Rutas: Calificaciones y Reportes ────────────────────────────────────────

@app.get("/calificaciones/{estacion_id}")
def calificaciones_estacion(estacion_id: str, db: Session = Depends(get_db)):
    cals = db.query(Calificacion).filter(Calificacion.estacion_ocm_id == estacion_id).order_by(Calificacion.fecha.desc()).all()
    promedio = round(sum(c.puntaje for c in cals) / len(cals), 1) if cals else 0
    return {"promedio": promedio, "total": len(cals), "calificaciones": cals}

@app.post("/calificaciones")
def calificar(data: dict, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if not (1 <= data.get("puntaje", 0) <= 5): raise HTTPException(400, "Puntaje entre 1 y 5")
    cal = Calificacion(usuario_id=current_user.id, **data)
    db.add(cal); db.commit()
    return {"ok": True}

@app.get("/reportes/{estacion_id}")
def reportes_estacion(estacion_id: str, db: Session = Depends(get_db)):
    return db.query(Reporte).filter(Reporte.estacion_ocm_id == estacion_id, Reporte.estado == "abierto").order_by(Reporte.fecha.desc()).limit(10).all()

@app.post("/reportes")
def reportar(data: dict, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    rep = Reporte(usuario_id=current_user.id, **data)
    db.add(rep); db.commit()
    return {"ok": True}

# ─── Rutas: Favoritos ─────────────────────────────────────────────────────────

@app.get("/favoritos")
def listar_favoritos(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": f.id, "estacion_ocm_id": f.estacion_ocm_id, "estacion_nombre": f.estacion_nombre} for f in current_user.favoritos]

@app.post("/favoritos")
def agregar_favorito(data: dict, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    existe = db.query(Favorito).filter(Favorito.usuario_id == current_user.id, Favorito.estacion_ocm_id == data.get("estacion_ocm_id")).first()
    if existe: raise HTTPException(400, "Ya está en favoritos")
    db.add(Favorito(usuario_id=current_user.id, **data)); db.commit()
    return {"ok": True}

@app.delete("/favoritos/{estacion_id}")
def quitar_favorito(estacion_id: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = db.query(Favorito).filter(Favorito.usuario_id == current_user.id, Favorito.estacion_ocm_id == estacion_id).first()
    if not fav: raise HTTPException(404, "No encontrado")
    db.delete(fav); db.commit()
    return {"ok": True}

# ─── Rutas: Estado y reservas públicas ────────────────────────────────────────

@app.get("/estado/{estacion_id}")
def obtener_estado_estacion(estacion_id: str, db: Session = Depends(get_db)):
    propia = db.query(EstacionPropia).filter(EstacionPropia.id == estacion_id).first()
    if propia and not propia.activa:
        return {"estado": "mantenimiento"}
    reporte_mantenimiento = db.query(Reporte).filter(
        Reporte.estacion_ocm_id == estacion_id,
        Reporte.estado == "abierto",
        Reporte.tipo.in_(["averia", "fuera_servicio"])
    ).first()
    if reporte_mantenimiento:
        return {"estado": "mantenimiento"}
    ahora = datetime.now(timezone.utc)
    reserva_activa = db.query(Reserva).filter(
        Reserva.estacion_ocm_id == estacion_id,
        Reserva.estado == "activa",
        Reserva.fecha_hora_inicio <= ahora,
        Reserva.fecha_hora_fin >= ahora
    ).first()
    if reserva_activa:
        return {"estado": "reservada", "reservado_por": reserva_activa.usuario.nombre}
    return {"estado": "disponible"}

# ─── Rutas: Admin (Terpel) ────────────────────────────────────────────────────

# Usuarios
@app.get("/admin/usuarios")
def admin_listar_usuarios(admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Usuario).order_by(Usuario.created_at.desc()).all()

@app.get("/admin/estadisticas")
def admin_estadisticas(admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    return {"total_usuarios": db.query(Usuario).count(), "total_reportes": db.query(Reporte).count(), "total_calificaciones": db.query(Calificacion).count()}

@app.get("/admin/reportes")
def admin_reportes(admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Reporte).order_by(Reporte.fecha.desc()).limit(50).all()

@app.patch("/admin/reportes/{rid}/resolver")
def resolver_reporte(rid: str, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    r = db.query(Reporte).filter(Reporte.id == rid).first()
    if not r: raise HTTPException(404, "Reporte no encontrado")
    r.estado = "resuelto"; db.commit()
    return {"ok": True}

@app.get("/admin/estaciones")
def listar_estaciones_propias(admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(EstacionPropia).order_by(EstacionPropia.created_at.desc()).all()

@app.post("/admin/estaciones")
def crear_estacion_propia(data: dict, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    est = EstacionPropia(**data)
    db.add(est); db.commit(); db.refresh(est)
    return {"ok": True, "id": est.id}

@app.patch("/admin/estaciones/{eid}/estado")
def cambiar_estado_estacion_propia(eid: str, data: dict, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    est = db.query(EstacionPropia).filter(EstacionPropia.id == eid).first()
    if not est: raise HTTPException(404, "Estación no encontrada")
    if "activa" in data: est.activa = data["activa"]; db.commit()
    return {"ok": True}

@app.delete("/admin/estaciones/{eid}")
def eliminar_estacion_propia(eid: str, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    est = db.query(EstacionPropia).filter(EstacionPropia.id == eid).first()
    if not est: raise HTTPException(404, "Estación no encontrada")
    est.activa = False; db.commit()
    return {"ok": True}

# ─── Admin: Gestión de Reservas (todas) ──────────────────────────────────────

@app.get("/admin/reservas")
def admin_listar_reservas(admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Reserva).order_by(Reserva.created_at.desc()).all()

@app.put("/admin/reservas/{rid}")
def admin_actualizar_reserva(rid: str, data: ReservaUpdate, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    r = db.query(Reserva).filter(Reserva.id == rid).first()
    if not r: raise HTTPException(404, "Reserva no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(r, key, value)
    db.commit(); db.refresh(r)
    return r

@app.delete("/admin/reservas/{rid}")
def admin_eliminar_reserva(rid: str, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    r = db.query(Reserva).filter(Reserva.id == rid).first()
    if not r: raise HTTPException(404, "Reserva no encontrada")
    db.delete(r); db.commit()
    return {"ok": True}

# ─── Rutas: Mapa y Enrutamiento ───────────────────────────────────────────────

@app.get("/buscar-ruta")
def buscar_ruta(user_lat: float, user_lon: float, dest_lat: float, dest_lon: float):
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{user_lon},{user_lat};{dest_lon},{dest_lat}?overview=full&geometries=geojson"
    try:
        data = requests.get(osrm_url, timeout=10).json()
        if "routes" not in data or not data["routes"]: raise HTTPException(500, "No se pudo calcular la ruta vial")
        return data["routes"][0]["geometry"]
    except:
        raise HTTPException(503, "Error conectando con OSRM")

@app.get("/planificar-viaje")
def planificar_viaje(origen_lat: float, origen_lon: float, destino_lat: float, destino_lon: float, autonomia_km: float = 300):
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{origen_lon},{origen_lat};{destino_lon},{destino_lat}?overview=full&geometries=geojson&steps=true"
    try:
        ruta = requests.get(osrm_url, timeout=10).json()["routes"][0]
        distancia_total_km = ruta["distance"] / 1000
        paradas_necesarias = max(1, int(distancia_total_km / (autonomia_km * 0.8)))
        coords = ruta["geometry"]["coordinates"]
        sugerencias = []
        for i in range(1, paradas_necesarias + 1):
            idx = int((i / (paradas_necesarias + 1)) * len(coords))
            punto = coords[min(idx, len(coords) - 1)]
            ocm_resp = requests.get(f"https://api.openchargemap.io/v3/poi/?output=json&countrycode=CO&latitude={punto[1]}&longitude={punto[0]}&distance=5&distanceunit=KM&compact=true&verbose=false&maxresults=3&key=750370f3-3d40-4082-b93c-904118ab1dc8", timeout=8).json()
            for st in ocm_resp[:2]:
                sugerencias.append({
                    "id": str(st.get("ID", "")),
                    "nombre": st.get("AddressInfo", {}).get("Title", "Estación"),
                    "lat": st.get("AddressInfo", {}).get("Latitude"),
                    "lon": st.get("AddressInfo", {}).get("Longitude"),
                    "parada_numero": i
                })
        return {
            "distancia_total_km": round(distancia_total_km, 1),
            "duracion_min": round(ruta["duration"] / 60, 0),
            "paradas_sugeridas": paradas_necesarias,
            "geometry": ruta["geometry"],
            "estaciones_en_ruta": sugerencias
        }
    except:
        raise HTTPException(503, "Error conectando con OSRM u OCM")