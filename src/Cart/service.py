import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.db.models import Cart, CartItem, MenuItem, MenuItemSize
from .schemas import CartItemCreate, CartRead, CartItemRead


class CartService:

    async def _build_response(self, cart: Cart, session: AsyncSession) -> CartRead:
        items = []
        for item in cart.items:
            menu_item = await session.get(MenuItem, item.menu_item_uid)
            menu_item_size = await session.get(MenuItemSize, item.menu_item_size_uid)
            items.append(CartItemRead(
                uid=item.uid,
                menu_item_uid=item.menu_item_uid,
                menu_item_size_uid=item.menu_item_size_uid,
                menu_item_name=menu_item.name if menu_item else "Unknown",
                pizza_size=menu_item_size.pizza_size if menu_item_size else "Unknown",
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=round(item.quantity * item.unit_price, 2),
            ))
        return CartRead(
            uid=cart.uid,
            items=items,
            total=round(sum(i.subtotal for i in items), 2),
        )

    async def get_or_create_cart(self, user_uid: uuid.UUID, session: AsyncSession) -> Cart:
        result = await session.exec(select(Cart).where(Cart.user_uid == user_uid))
        cart = result.first()
        if cart is None:
            cart = Cart(user_uid=user_uid)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        return cart

    async def get_cart(self, user_uid: uuid.UUID, session: AsyncSession) -> CartRead:
        cart = await self.get_or_create_cart(user_uid, session)
        return await self._build_response(cart, session)

    async def add_item(self, user_uid: uuid.UUID, data: CartItemCreate, session: AsyncSession) -> CartRead:
        menu_item = await session.get(MenuItem, data.menu_item_uid)
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        if not menu_item.is_available:
            raise HTTPException(status_code=400, detail="Menu item is not available")

        menu_item_size = await session.get(MenuItemSize, data.menu_item_size_uid)
        if not menu_item_size or menu_item_size.menu_item_uid != menu_item.uid:
            raise HTTPException(status_code=400, detail="Invalid size for this menu item")

        if data.quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be at least 1")

        cart = await self.get_or_create_cart(user_uid, session)

        # If the same size is already in the cart, increase quantity instead of duplicating
        result = await session.exec(
            select(CartItem).where(
                CartItem.cart_uid == cart.uid,
                CartItem.menu_item_size_uid == data.menu_item_size_uid,
            )
        )
        existing = result.first()
        if existing:
            existing.quantity += data.quantity
            session.add(existing)
        else:
            session.add(CartItem(
                cart_uid=cart.uid,
                menu_item_uid=data.menu_item_uid,
                menu_item_size_uid=data.menu_item_size_uid,
                quantity=data.quantity,
                unit_price=menu_item_size.price,
            ))

        await session.commit()
        await session.refresh(cart)
        return await self._build_response(cart, session)

    async def update_item_quantity(
        self, user_uid: uuid.UUID, item_uid: uuid.UUID, quantity: int, session: AsyncSession
    ) -> CartRead:
        cart = await self.get_or_create_cart(user_uid, session)
        result = await session.exec(
            select(CartItem).where(CartItem.uid == item_uid, CartItem.cart_uid == cart.uid)
        )
        item = result.first()
        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        if quantity <= 0:
            await session.delete(item)
        else:
            item.quantity = quantity
            session.add(item)

        await session.commit()
        await session.refresh(cart)
        return await self._build_response(cart, session)

    async def remove_item(self, user_uid: uuid.UUID, item_uid: uuid.UUID, session: AsyncSession) -> CartRead:
        cart = await self.get_or_create_cart(user_uid, session)
        result = await session.exec(
            select(CartItem).where(CartItem.uid == item_uid, CartItem.cart_uid == cart.uid)
        )
        item = result.first()
        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        await session.delete(item)
        await session.commit()
        await session.refresh(cart)
        return await self._build_response(cart, session)

    async def clear_cart(self, user_uid: uuid.UUID, session: AsyncSession) -> dict:
        cart = await self.get_or_create_cart(user_uid, session)
        for item in cart.items:
            await session.delete(item)
        await session.commit()
        return {"message": "Cart cleared successfully"}
