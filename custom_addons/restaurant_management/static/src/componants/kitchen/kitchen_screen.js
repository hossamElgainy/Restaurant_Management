/** @odoo-module **/
import { Component, onWillStart, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class KitchenScreen extends Component {
    setup() {

        this.orm = useService("orm");

        this.state = useState({
            orders: [],
            loading: true,
            selectedState: "all",
        });

        onWillStart(async () => {
            await this.loadOrders();
            this.interval = setInterval(
                () => this.loadOrders(),
                60000
            );
        });

        onWillUnmount(() => {
            if (this.interval) {
                clearInterval(this.interval);
            }
        });
    }

    loadOrders = async () => {
        if (!this.orm) {
            console.error("ORM service not available");
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
        try {
            this.state.orders = await this.orm.call(
                "restaurant.order",
                "get_kitchen_orders",
                []
            );
        } catch (error) {
            console.error("Error loading orders:", error);
        } finally {
            this.state.loading = false;
        }
    }

    setFilter = (ev) => {
        const selectedState = ev.currentTarget.dataset.state;
        this.state.selectedState = selectedState;
    }

    get filteredOrders() {
        if (this.state.selectedState === "all") {
            return this.state.orders;
        }
        return this.state.orders.filter(
            order => order.state === this.state.selectedState
        );
    }

    startOrder = async (orderId) => {
        if (!this.orm) {
            console.error("ORM service not available");
            return;
        }
        await this.orm.call(
            "restaurant.order",
            "action_start_preparing",
            [[orderId]]
        );
        await this.loadOrders();
    }

    markReady = async (orderId) => {
        if (!this.orm) {
            console.error("ORM service not available");
            return;
        }
        await this.orm.call(
            "restaurant.order",
            "action_mark_ready",
            [[orderId]]
        );
        await this.loadOrders();
    }
}

KitchenScreen.template = "restaurant_management.kitchen_screen";

registry.category("actions").add(
    "restaurant_management.kitchen_screen",
    KitchenScreen
);