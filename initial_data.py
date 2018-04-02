from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Technology, Machine

engine = create_engine('sqlite:///printingmachines.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


User1 = User(name="Victor Nhem", email="sna_07@yahoo.com")
session.add(User1)
session.commit()


technology1 = Technology(user_id=1, name="Stereolithography")
session.add(technology1)
session.commit()


machine1 = Machine(user_id=1, name="Form2", manufacturer="Formlabs", price="$3,350", feature="Industrial quality 3D printing made accessible, the Form 2 delivers high-resolution prints at a fraction of the cost", technology=technology1)
session.add(machine1)
session.commit()


machine2 = Machine(user_id=1, name="FlashForge Hunter DLP Resin 3D Printer", manufacturer="FlashForge", price="$3,499", feature="It can create prints with layer resolutions of 12.5, 25, and 50 microns and prints from its aluminum resin tray with pre-installed vat film that supports multiple types of resin", technology=technology1)
session.add(machine2)
session.commit()


machine3 = Machine(user_id=1, name="Moai", manufacturer="PeoPoly", price="$1,250", feature="The Moai is powered by an ST 32-bit ARM processor, capable of interpreting Gcode and running the machine incredibly fast, allowing for high precision movements without having to increase print time", technology=technology1)
session.add(machine3)
session.commit()


machine4 = Machine(user_id=1, name="XYZprinting Nobel 1.0A", manufacturer="XYZprinting", price="$1,799", feature="It has an enhanced Laser Scanning Unit that improves the resolution of the engine's laser to 130 microns on the X/Y axis, while also providing resolution options of 25, 50, and 100 microns on the Z axis", technology=technology1)
session.add(machine4)
session.commit()


machine5 = Machine(user_id=1, name="Dazz 3d S130", manufacturer="Dazz3D", price="$3,900", feature="It offers a relatively small build size of 130 x 130 x 180 mm and a high print resolution that is ideal for prototyping, dental or jewelry applications, printing architectural models and more", technology=technology1)
session.add(machine5)
session.commit()


technology2 = Technology(user_id=1, name="Fused Deposition Modeling")
session.add(technology2)
session.commit()


machine1 = Machine(user_id=1, name="TAZ 6", manufacturer="LulzBot", price="$2,500", feature="It is self-leveling and self-cleaning, while also taking advantage of a modular tool head design for flexible and multi-material upgrades", technology=technology2)
session.add(machine1)
session.commit()


machine2 = Machine(user_id=1, name="Replicator+", manufacturer="MakerBot", price="$2,499", feature="The Replicator+ features a build volume of 11.6 x 7.6 x 6.5in; a cubic build volume of 573 cubic inch; a layer resolution of 100-400 microns", technology=technology2)
session.add(machine2)
session.commit()


machine3 = Machine(user_id=1, name="M200", manufacturer="Zortrax", price="$1,990", feature="It prints up to 200 x 200 x 185 mm (7.87 L x 7.87 W x 7.28 Hin, and has user-friendly Z-suite software", technology=technology2)
session.add(machine3)
session.commit()


machine4 = Machine(user_id=1, name="XYZprinting da Vinci Jr. 2.0", manufacturer="XYZprinting", price="$449", feature="It features Fused Filament Fabrication printing technology; a build volume of 5.9 x 5.9 x 5.9 in; a layer resolution of 200 to 400 microns; and the ability to utilize 1.75mm PLA filaments via its auto-loading filament system", technology=technology2)
session.add(machine4)
session.commit()


machine5 = Machine(user_id=1, name="N2 PLUS DUAL EXTRUDER", manufacturer="RAISE3D", price="$3,899", feature="It has huge 24in tall build platform, V2 hot end assembly, and print resolution from 0.01mm - 0.25mm", technology=technology2)
session.add(machine5)
session.commit()


technology3 = Technology(user_id=1, name="Selective Laser Sintering")
session.add(technology3)
session.commit()


machine1 = Machine(user_id=1, name="Fuse 1", manufacturer="Formlabs", price="$9,999", feature="It has 165 x 165 x 320 mm build volume for bigger parts and higher throughput", technology=technology3)
session.add(machine1)
session.commit()


machine2 = Machine(user_id=1, name="Lisa SLS 3D", manufacturer="Sinterit", price="$5,837", feature="It is plug, and play, no supports, and immediate part functionality", technology=technology3)
session.add(machine2)
session.commit()


machine3 = Machine(user_id=1, name="Natural Robotics VIT SLS", manufacturer="Natural Robotics", price="$11,696", feature="It allows for quick yet detailed prototyping. Also, SLS enables 3D printing complex geometric shapes without the need for support structures", technology=technology3)
session.add(machine3)
session.commit()


machine4 = Machine(user_id=1, name="Sintratec S1", manufacturer="Sintratec", price="$11,154", feature="It is a Swiss manufacturer, doesn't require special ventilation systems, and no need for support structures", technology=technology3)
session.add(machine4)
session.commit()

print("add machines!")
