from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.schemas.order import OrderResponse

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post(
    "/place",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def place_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    total_amount = 0

    for item in cart_items:
        total_amount += item.product.price * item.quantity

    order = Order(
        user_id=current_user.id,
        total_amount=total_amount
    )

    db.add(order)
    db.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price
        )

        db.add(order_item)

        item.product.stock -= item.quantity

    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(order)

    return order

@router.get(
    "/",
    response_model=list[OrderResponse]
)
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()

    return orders