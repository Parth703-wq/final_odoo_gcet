from app.core.database import SessionLocal
from app.models.product import Product

def update_images():
    db = SessionLocal()
    updates = {
        1: '/uploads/products/canon_eos_r6.png',
        2: '/uploads/products/macbook_pro_16.png',
        3: '/uploads/products/mavic_3_pro.png',
        4: '/uploads/products/projector_4k.png',
        5: '/uploads/products/gaming_pc.png',
        6: '/uploads/products/aeron_chair.png',
        7: '/uploads/products/sony_a7.png',
        8: '/uploads/products/makita_kit.png',
        11: '/uploads/products/laptop_stand.png'
    }
    
    for pid, url in updates.items():
        p = db.query(Product).filter(Product.id == pid).first()
        if p:
            p.image_url = url
            db.add(p)
            print(f'Updated product {pid}: {p.name}')
    
    db.commit()
    db.close()

if __name__ == '__main__':
    update_images()
