#!/usr/bin/env python3
"""
Tests for Cart controller implementation.
Project:     Automated Testing and Dynamic Analysis (ATA) - project 1
Author:      Lucie Svobodova, xsvobo1x
University:  FIT BUT, 2022/2023
"""
import sys
from cartctl import CartCtl, Status as CartCtlStatus, PrioRequestTimeout
from cart import Cart, CargoReq, Status as CartStatus, CartError
from jarvisenv import Jarvis
import unittest

def log(msg):
    "simple logging"
    print('  %s' % msg)

class TestCartRequests(unittest.TestCase):

    def test_happy(self):
        "Happy-path test"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for unloading the cart"
            # put some asserts here
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            # put some asserts here
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            cargo_req.context = 'unloaded'
            if cargo_req.content == 'helmet':
                self.assertEqual('B', c.pos)
            if cargo_req.content == 'heart':
                self.assertEqual('A', c.pos)
            #if cargo_req.content.startswith('bracelet'):
            #    self.assertEqual('C', c.pos)
            if cargo_req.content == 'braceletR':
                self.assertEqual('A', c.pos)
            if cargo_req.content == 'braceletL':
                self.assertEqual('C', c.pos)

        # Setup Cart
        # 4 slots, 150 kg max payload capacity, 2=max debug
        cart_dev = Cart(4, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        helmet = CargoReq('A', 'B', 20, 'helmet')
        helmet.onload = on_load
        helmet.onunload = on_unload

        heart = CargoReq('C', 'A', 40, 'heart')
        heart.onload = on_load
        heart.onunload = on_unload

        braceletR = CargoReq('D', 'A', 40, 'braceletR')
        braceletR.onload = on_load
        braceletR.onunload = on_unload

        braceletL = CargoReq('D', 'C', 40, 'braceletL')
        braceletL.onload = on_load
        braceletL.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(10, add_load, (c,helmet))
        Jarvis.plan(45, add_load, (c,heart))
        Jarvis.plan(40, add_load, (c,braceletR))
        Jarvis.plan(25, add_load, (c,braceletL))
        
        # Exercise + Verify indirect output
        #   SUT is the Cart.
        #   Exercise means calling Cart.request in different time periods.
        #   Requests are called by add_load (via plan and its scheduler).
        #   Here, we run the plan.
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', helmet.context)
        self.assertEqual('unloaded', heart.context)
        self.assertEqual('unloaded', braceletR.context)
        self.assertEqual('unloaded', braceletL.context)
    
    def test_ceg1_combine1(self):
        "Test: Ceg1_Combine1, covers Ceg1, Combine1"

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.fail("Cart shouldn't be moving.")

        # Setup Cart
        cart_dev = Cart(1, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)
        
        # Setup Plan
        Jarvis.reset_scheduler()
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_ceg2(self):
        "Test: Ceg2"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Cart shouldn't be loaded because the request is too heavy.")

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Cart shouldn't contain any requests.")

        # Setup Cart
        cart_dev = Cart(2, 50, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('D', 'B', 74, 'GLASS74x82')
        req1.onload = on_load
        req1.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(1, add_load, (c,req1))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_ceg3(self):
        "Test: Ceg3"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)
            self.assertFalse(cargo_req.prio)
            Jarvis._sleep(59)
            c.update_prio_requests()
            log('%d: After 59 seconds: %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            self.assertFalse(cargo_req.prio)
            Jarvis._sleep(1)
            c.update_prio_requests()
            log('%d: After one more socend: %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            self.assertTrue(cargo_req.prio)
            Jarvis._sleep(60)
            c.update_prio_requests()
            log('%d: After another 60 seconds: %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            self.assertTrue(cargo_req.prio)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Cart shouldn't be loaded because the request waited too long.")

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Cart shouldn't contain any requests.")

        # Setup Cart
        cart_dev = Cart(2, 50, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('D', 'B', 1, 'baseball bat')
        req1.onload = on_load
        req1.onunload = on_unload
        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(0, add_load, (c,req1))

        # Exercise + Verify indirect output
        self.assertRaises(PrioRequestTimeout, Jarvis.run)
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)    

    def test_ceg4(self):
        "Test: Ceg4"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)
            self.assertFalse(cargo_req.prio)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('WOOD', cargo_req.content)
            self.assertIn(cargo_req, c.slots)
            self.assertEqual('A', c.pos)
            self.assertFalse(cargo_req.prio)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertFalse(cargo_req.prio)
            self.assertEqual('loaded', cargo_req.context)
            self.assertEqual('WOOD', cargo_req.content)
            self.assertEqual('B', c.pos)
            self.assertNotIn(cargo_req, c.slots)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(2, 500, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('A', 'B', 100, 'WOOD')
        req1.onload = on_load
        req1.onunload = on_unload
        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(55, add_load, (c,req1))

        # Exercise + Verify indirect output
        Jarvis.run()        
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)    

    def test_ceg5(self):
        "Test: Ceg5"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)
            self.assertFalse(cargo_req.prio)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)
            Jarvis._sleep(10)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('full box of croissants', cargo_req.content)
            self.assertIn(cargo_req, c.slots)
            self.assertEqual('C', c.pos)
            self.assertTrue(cargo_req.prio)

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertTrue(cargo_req.prio)
            #self.assertEqual('loaded', cargo_req.context)
            self.assertEqual('full box of croissants', cargo_req.content)
            self.assertEqual('A', c.pos)
            self.assertNotIn(cargo_req, c.slots)
            self.assertEqual(cargo_req.context.status, CartCtlStatus.UnloadOnly)
            
        # Setup Cart
        cart_dev = Cart(4, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('C', 'A', 50, 'full box of croissants')
        req1.context = c
        req1.onload = on_load
        req1.onunload = on_unload
        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(1000, add_load, (c,req1))

        # Exercise + Verify indirect output
        Jarvis.run()        
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)    

    def test_combine2(self):
        "Test: Combine2"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('rubber duck', cargo_req.content)
            self.assertEqual('A', c.pos)
            self.assertIn(cargo_req, c.slots)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            self.assertEqual('rubber duck', cargo_req.content)
            self.assertEqual('D', c.pos)
            self.assertNotIn(cargo_req, c.slots)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(1, 500, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('A', 'D', 500, 'rubber duck')
        req1.onload = on_load
        req1.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #          when  event  called_with_params
        Jarvis.plan(5, add_load, (c,req1))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine3(self):
        "Test: Combine3"

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.fail("Cart shouldn't be moving.")

        # Setup Cart
        cart_dev = Cart(2, 50, 2)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Plan
        Jarvis.reset_scheduler()
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)
        
    def test_combine4(self):
        "Test: Combine4"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('SHS647444', cargo_req.content)
            self.assertIn(cargo_req, c.slots)
            self.assertEqual('B', c.pos)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            self.assertEqual('SHS647444', cargo_req.content)
            self.assertNotIn(cargo_req, c.slots)
            self.assertEqual('D', c.pos)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(2, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('B', 'D', 150, 'SHS647444')
        req1.onload = on_load
        req1.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(30, add_load, (c,req1))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine5(self):
        "Test: Combine5"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertIn(cargo_req, c.slots)
            if cargo_req.content == 'peanut butter':
                self.assertEqual('C', c.pos)
            if cargo_req.content == 'nutella':
                self.assertEqual('B', c.pos)
            if cargo_req.content == 'coffee':
                self.assertEqual('C', c.pos)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            self.assertNotIn(cargo_req, c.slots)
            if cargo_req.content == 'peanut butter':
                self.assertEqual('A', c.pos)
            if cargo_req.content == 'nutella':
                self.assertEqual('D', c.pos)
            if cargo_req.content == 'coffee':
                self.assertEqual('D', c.pos)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(2, 500, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('C', 'A', 200, 'peanut butter')
        req1.onload = on_load
        req1.onunload = on_unload

        req2 = CargoReq('B', 'D', 20, 'nutella')
        req2.onload = on_load
        req2.onunload = on_unload

        req3 = CargoReq('C', 'D', 10, 'coffee')
        req3.onload = on_load
        req3.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(1, add_load, (c,req1))
        Jarvis.plan(2, add_load, (c,req2))
        Jarvis.plan(70, add_load, (c,req3))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual('unloaded', req2.context)
        self.assertEqual('unloaded', req3.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine6(self):
        "Test: Combine6"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Request shouldn't be loaded because it is too heavy.")

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Request shouldn't be in the cart.")

        # Setup Cart
        cart_dev = Cart(4, 50, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('C', 'C', 60, 'rubber duck')
        req1.onload = on_load
        req1.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(5, add_load, (c,req1))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine7(self):
        "Test: Combine7"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('D', c.pos)
            self.assertIn(cargo_req, c.slots)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('B', c.pos)
            self.assertNotIn(cargo_req, c.slots)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(3, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('D', 'B', 50, 'bug')
        req1.onload = on_load
        req1.onunload = on_unload
        
        req2 = CargoReq('D', 'B', 100, 'feature')
        req2.onload = on_load
        req2.onunload = on_unload

        req3 = CargoReq('D', 'B', 100, 'creature')
        req3.onload = on_load
        req3.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(5, add_load, (c,req1))
        Jarvis.plan(6, add_load, (c,req2))
        Jarvis.plan(80, add_load, (c,req3))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual('unloaded', req2.context)
        self.assertEqual('unloaded', req3.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine8(self):
        "Test: Combine8"

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.fail("Cart shouldn't be moving.")

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Cart shouldn't be loading.")

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.fail("Cart shouldn't be unloading.")

        # Setup Cart
        cart_dev = Cart(3, 50, 2)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('A', 'D', 20, 'rubber duck')
        req1.onload = on_load
        req1.onunload = on_unload
        
        # Setup Plan
        Jarvis.reset_scheduler()
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine9(self):
        "Test: Combine9"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for unloading the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            if cargo_req.content == 'baby box' or cargo_req.content == 'christmas tree':
                self.assertEqual('B', c.pos)
            if cargo_req.content == 'pizza':
                self.assertEqual('C', c.pos)
            self.assertIn(cargo_req, c.slots)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            if cargo_req.content == 'baby box':
                self.assertEqual('D', c.pos)
            if cargo_req.content == 'christmas tree':
                self.assertEqual('A', c.pos)
            if cargo_req.content == 'pizza':
                self.assertEqual('B', c.pos)
            self.assertNotIn(cargo_req, c.slots)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(2, 50, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('B', 'D', 10, 'baby box')
        req1.onload = on_load
        req1.onunload = on_unload
        
        req2 = CargoReq('B', 'A', 40, 'christmas tree')
        req2.onload = on_load
        req2.onunload = on_unload

        req3 = CargoReq('C', 'B', 30, 'pizza')
        req3.onload = on_load
        req3.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(5, add_load, (c,req1))
        Jarvis.plan(6, add_load, (c,req2))
        Jarvis.plan(105, add_load, (c,req3))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual('unloaded', req2.context)
        self.assertEqual('unloaded', req3.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine10(self):
        "Test: Combine10"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertIn(cargo_req, c.slots)
            if cargo_req.content == 'PKG007':
                self.assertEqual('C', c.pos)
            if cargo_req.content == 'PKG6557' or cargo_req.content == 'PKG6559':
                self.assertEqual('A', c.pos)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertNotIn(cargo_req, c.slots)
            self.assertEqual('loaded', cargo_req.context)
            if cargo_req.content == 'PKG007':
                self.assertEqual('D', c.pos)
            if cargo_req.content == 'PKG6557':
                self.assertEqual('B', c.pos)
            if cargo_req.content == 'PKG6559':
                self.assertEqual('A', c.pos)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(1, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('C', 'D', 6, 'PKG007')
        req1.onload = on_load
        req1.onunload = on_unload
        
        req2 = CargoReq('A', 'B', 150, 'PKG6557')
        req2.onload = on_load
        req2.onunload = on_unload
        
        req3 = CargoReq('A', 'A', 60, 'PKG6559')
        req3.onload = on_load
        req3.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(0, add_load, (c,req1))
        Jarvis.plan(75, add_load, (c,req2))
        Jarvis.plan(77, add_load, (c,req3))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual('unloaded', req2.context)
        self.assertEqual('unloaded', req3.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine11(self):
        "Test: Combine11"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)
            Jarvis._sleep(10)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertIn(cargo_req, c.slots)
            self.assertEqual('chocolate', cargo_req.content)
            self.assertEqual('C', c.pos)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            self.assertEqual('chocolate', cargo_req.content)
            self.assertNotIn(cargo_req, c.slots)
            self.assertEqual('A', c.pos)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(2, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('C', 'A', 1, 'chocolate')
        req1.onload = on_load
        req1.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(666, add_load, (c,req1))
        
        # Exercise + Verify indirect output
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine12(self):
        "Test: Combine12"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            if cargo_req.content == 'CZ-29861':
                self.assertEqual('A', c.pos)
            if cargo_req.content == 'AU-875684':
                self.assertEqual('B', c.pos)
            self.assertIn(cargo_req, c.slots)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            self.assertNotIn(cargo_req, c.slots)
            self.assertEqual('D', c.pos)
            cargo_req.context = 'unloaded'

        # Setup Cart
        cart_dev = Cart(2, 500, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('A', 'D', 250, 'CZ-29861')
        req1.onload = on_load
        req1.onunload = on_unload
        
        req2 = CargoReq('B', 'D', 250, 'AU-875684')
        req2.onload = on_load
        req2.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(10, add_load, (c,req1))
        Jarvis.plan(12, add_load, (c,req2))
        
        # Exercise + Verify indirect output
        log(cart_dev)
        Jarvis.run()

        # Verify direct output
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual('unloaded', req2.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine13(self):
        "Test: Combine13"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)
            Jarvis._sleep(10)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertIn(cargo_req, c.slots)
            self.assertEqual('D', c.pos)
            if cargo_req.content == 'req3':
                c.empty()
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            self.assertEqual('A', c.pos)
            self.assertNotIn(cargo_req, c.slots)
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(2, 50, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('D', 'A', 20, 'req1')
        req1.onload = on_load
        req1.onunload = on_unload
        
        req2 = CargoReq('D', 'A', 30, 'req2')
        req2.onload = on_load
        req2.onunload = on_unload

        req3 = CargoReq('D', 'A', 25, 'req3')
        req3.onload = on_load
        req3.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(0, add_load, (c,req1))
        Jarvis.plan(1, add_load, (c,req2))
        Jarvis.plan(62, add_load, (c,req3))
        
        # Exercise + Verify indirect output
        log(cart_dev)
        self.assertRaises(PrioRequestTimeout, Jarvis.run)
        # Verify direct output without exception
        #self.assertTrue(cart_dev.empty())
        #self.assertEqual('unloaded', req1.context)
        #self.assertEqual('unloaded', req2.context)
        #self.assertEqual('unloaded', req3.context)
        #self.assertEqual(cart_dev.status, CartStatus.Idle)
        #self.assertEqual(c.status, CartCtlStatus.Idle)

    def test_combine14(self):
        "Test: Combine14"

        def add_load(c: CartCtl, cargo_req: CargoReq):
            "callback for schedulled load"
            log('%d: Requesting %s at %s' % \
                (Jarvis.time(), cargo_req, cargo_req.src))
            c.request(cargo_req)

        def on_move(c: Cart):
            "callback for moving the cart"
            log('%d: Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
            self.assertEqual(c.status, CartStatus.Moving)

        def on_load(c: Cart, cargo_req: CargoReq):
            "callback for loading the cart"
            log('%d: Cart at %s: loading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            if cargo_req.content == 'coffee' or cargo_req.content == 'code':
                c.empty()
            self.assertIn(cargo_req, c.slots)
            if cargo_req.content == 'coffee':
                self.assertEqual('D', c.pos)
            if cargo_req.content == 'code':
                self.assertEqual('C', c.pos)
            cargo_req.context = 'loaded'

        def on_unload(c: Cart, cargo_req: CargoReq):
            "callback for unloading the cart"
            log('%d: Cart at %s: unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
            log(c)
            self.assertEqual('loaded', cargo_req.context)
            self.assertNotIn(cargo_req, c.slots)
            if cargo_req.content == 'coffee':
                self.assertEqual('A', c.pos)
            if cargo_req.content == 'code':
                self.assertEqual('B', c.pos)
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(2, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        c = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        req1 = CargoReq('D', 'A', 150, 'coffee')
        req1.onload = on_load
        req1.onunload = on_unload
        
        req2 = CargoReq('C', 'B', 150, 'code')
        req2.onload = on_load
        req2.onunload = on_unload

        # Setup Plan
        Jarvis.reset_scheduler()
        #         when  event     called_with_params
        Jarvis.plan(2, add_load, (c,req1))
        Jarvis.plan(111, add_load, (c,req2))
        
        # Exercise + Verify
        log(cart_dev)
        Jarvis.run()
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', req1.context)
        self.assertEqual('unloaded', req2.context)
        self.assertEqual(cart_dev.status, CartStatus.Idle)
        self.assertEqual(c.status, CartCtlStatus.Idle)
    

if __name__ == "__main__":
    unittest.main()
