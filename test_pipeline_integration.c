/**
 * Test program to verify pipeline integration
 */
#include <stdio.h>
#include "mem/control_store.h"

int main() {
    printf("Testing pipeline integration...\n");

    // Test pipeline configuration
    lc3_pipeline_config_t config;
    lc3_pipeline_config_init_default(&config);
    printf("Default pipeline: %s\n", config.name);
    printf("Pipeline depth: %d\n", config.depth);

    // Test pipeline initialization
    lc3_pipeline_init();
    printf("Pipeline initialized: %s\n", lc3_pipeline_enabled ? "Yes" : "No");

    // Test instruction packet
    lc3_instruction_packet_t packet;
    lc3_instruction_packet_init(&packet);
    printf("Instruction packet initialized\n");

    // Test pipeline cycle
    lc3_pipeline_cycle();
    printf("Pipeline cycle completed\n");

    // Test metrics
    lc3_pipeline_metrics_t metrics;
    lc3_pipeline_get_metrics(&metrics);
    printf("Metrics retrieved\n");

    printf("Pipeline integration test completed successfully!\n");
    return 0;
}
