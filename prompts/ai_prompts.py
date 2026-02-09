class AIPrompts:
    @staticmethod
    def get_tour_constraint_prompt(
        user_query: str, message_history: list, allowed_cities: list
    ) -> str:
        return f"""
                INPUT:
                user query : {user_query}
                message history: {message_history}

                Role: You are an AI assistant to retrieve the necessary entity
                from the above given user query and provide in the following json 
                format. We have got only 5 cities in the database: {allowed_cities}.
                Make sure to consider city full names.

                Note: check message history for existing entities.
                """

    @staticmethod
    def get_missing_constraints_prompt(
        missing_constraints: list, allowed_cities: list
    ) -> str:
        return f"""
                INPUT:
                missing constraints: {missing_constraints}
                allowed cities: {allowed_cities}

                Role: You are an AI assistant to respond to the user politely to fill the missing constraints to continue the tour planning.
                Promote our tour package for: {', '.join(allowed_cities)}.
                """

    @staticmethod
    def get_planning_prompt(
        user_query: str,
        metadata: dict,
        attractions: list,
        travel: list,
        hotels: list,
    ) -> str:
        return f"""
            You are an expert tour planner. Create a {metadata["days"]}-day tour plan from {metadata["from_city"]} to {metadata["to_city"]}. 
            
            USER QUERY: {user_query}
            
            DATA:
            - Attractions: {attractions}
            - Travel Info: {travel}
            - Hotels: {hotels}

            INSTRUCTIONS:
            1. {metadata["days"]}-day itinerary.
            2. Specific timings.
            3. Best hotel from data.
            4. Travel mode/time.
            5. Use ONLY provided info.
            6. Title: "Tour Plan for {metadata["from_city"]} to {metadata["to_city"]}"
            """
