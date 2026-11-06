import pytest
from core.nlp import analyze, intent, entities
from core.dialogue import initial, process
from core.orders import item, totals
from core.receipt import receipt

CASES=[
("hola","saludar"),("adiós","despedirse"),("menú","consultar_menu"),("menú infantil","consultar_menu_infantil"),
("precio de hawaiana","consultar_precios"),("ingredientes de margarita","consultar_ingredientes"),
("recomiéndame una pizza","recomendar"),("promociones","consultar_promociones"),
("quiero pedir","iniciar_pedido"),("agrega pepperoni grande","agregar_producto"),
("cambia hawaiana a grande","modificar_pedido"),("quita margarita","eliminar_producto"),
("ver carrito","consultar_carrito"),("confirmar pedido","confirmar_pedido"),
("cancelar pedido","cancelar_pedido"),("horario","consultar_horario"),
("entrega a domicilio","consultar_domicilio"),("formas de pago","consultar_pago"),
("ayuda","ayuda"),("gracias","agradecer"),
("buenos días","saludar"),("hasta luego","despedirse"),("carta","consultar_menu"),
("menú para niños","consultar_menu_infantil"),("cuánto cuesta pepperoni","consultar_precios"),
("qué lleva hawaiana","consultar_ingredientes"),("ofertas","consultar_promociones"),
("mi pedido","consultar_carrito"),("a qué hora abren","consultar_horario"),
("qué puedes hacer","ayuda"),
]
@pytest.mark.parametrize("phrase,expected",CASES)
def test_intents(phrase,expected):assert intent(phrase)==expected

def test_entities():
    e=entities("quiero dos pizzas hawaianas grandes para 3 personas con presupuesto 500")
    assert e["cantidad"]==2 and e["tamano"]=="grande" and e["personas"]==3 and e["presupuesto"]==500

def test_context_size():
    s=initial();assert "tamaño" in process(s,"quiero una hawaiana").lower()
    process(s,"grande");assert len(s["cart"])==1 and s["cart"][0]["tamano"]=="grande"

def test_context_drink():
    s=initial();process(s,"quiero una hawaiana");process(s,"grande");process(s,"dos refrescos")
    assert len(s["cart"])==2 and s["cart"][1]["cantidad"]==2

def test_ambiguous_and_recovery():
    s=initial();process(s,"quiero una hawaiana");assert "tamaño" in process(s,"gigantesca").lower()
    process(s,"mediana");assert len(s["cart"])==1

def test_totals():
    cart=[item("hawaiana","grande",2),item("refresco",qty=2)]
    assert totals(cart,"domicilio",True)=={"subtotal":570,"descuento":50,"entrega":35,"total":555}

def test_modify_remove_cancel():
    s=initial();process(s,"agrega hawaiana grande");process(s,"cambia hawaiana a chica")
    assert s["cart"][0]["tamano"]=="chica"
    process(s,"quita hawaiana");assert not s["cart"]
    process(s,"agrega refresco");process(s,"cancelar pedido");assert not s["cart"]

def test_confirm_and_pdf():
    s=initial();process(s,"agrega pepperoni grande");process(s,"confirmar pedido")
    assert s["pending"]["kind"]=="service"
    process(s,"recoger");process(s,"confirmar pedido");assert s["confirmed"]
    assert receipt(s["cart"],s["service"]).startswith(b"%PDF")

def test_out_of_domain():
    s=initial();assert "no comprendí" in process(s,"cuál es la capital de venus").lower()

def test_restriction():
    s=initial();assert "no puedo garantizar" in process(s,"recomienda algo sin gluten").lower()

def test_invalid():
    with pytest.raises(ValueError):item("hawaiana","gigante")
    with pytest.raises(ValueError):item("refresco",qty=0)
