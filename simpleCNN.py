import tensorflow as tf
import os
import os.path
from mnist_deep import deepnn
from datetime import datetime

'''
SimpleCNN is a wrapper class of MNIST CNN demo code
'''
class SimpleCNN:
    def __init__(self, lr, log_path='tf_writer/', max_output_images=16):
        # clean log_path
        removeFileInDir(log_path)

        # Create the model
        
        self.x = tf.placeholder(tf.float32, [None, 784])
        # visualize X
        x_image = tf.reshape(self.x, [-1, 28, 28, 1])
        tf.summary.image('input_image', x_image, max_outputs=max_output_images)
        
        self.y_ = tf.placeholder(tf.float32, [None, 10])
        # visualize Y
        label_str = tf.as_string(self.y_)
        tf.summary.text('label', label_str)

        # Build the graph for the deep net
        y_conv, self.keep_prob = deepnn(self.x)
        self.output_prob_distribution = tf.nn.softmax(y_conv, name='out_prob_dist')
        

        with tf.name_scope('loss'):
            cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=self.y_,
                                                            logits=y_conv)
        cross_entropy = tf.reduce_mean(cross_entropy)
        tf.summary.scalar('cross_entropy', cross_entropy)

        with tf.name_scope('adam_optimizer'):
            self.train_step = tf.train.AdamOptimizer(lr).minimize(cross_entropy)

        with tf.name_scope('accuracy'):
            self.label = tf.argmax(self.y_, 1)
            correct_prediction = tf.equal(tf.argmax(y_conv, 1), self.label)
            correct_prediction = tf.cast(correct_prediction, tf.float32)
            self.accuracy = tf.reduce_mean(correct_prediction)
            tf.summary.scalar('accuracy',self.accuracy)

        self.merged = tf.summary.merge_all()

        all_vars = tf.global_variables()
        self.saver = tf.train.Saver(all_vars)

        self.sess = tf.Session()
        self.writer = tf.summary.FileWriter(log_path, self.sess.graph)
        self.sess.run(tf.global_variables_initializer())
   
    def reset(self):
        self.sess.run(tf.global_variables_initializer())
        print 'Re-Init the graph parameter'
 
    def train(self, mnist):
        for i in range(2000):
            batch = mnist.train.next_batch(1600)
            if i % 100 == 0:
                train_accuracy, prob_dist, label=self.sess.run([self.accuracy, self.output_prob_distribution, self.label], feed_dict={
                    self.x: batch[0], self.y_: batch[1], self.keep_prob:1.0})
                print(datetime.now().isoformat(), 'step %d, training accuracy %g' % (i, train_accuracy))
                for sample_idx in range(16):
                    sample_str = 'sample_idx=%d, Output_Probability_Distribution = [' % sample_idx
                    for class_idx in range(prob_dist.shape[1]):
                        sample_str += ("%.3f," % (prob_dist[sample_idx][class_idx]))
                    sample_str += ("] ")
                    sample_str += ("Label = %d" % label[sample_idx])
                    print sample_str

                merged = self.sess.run(self.merged, feed_dict={
                    self.x: batch[0], self.y_: batch[1], self.keep_prob:1.0})
                self.writer.add_summary(merged, i)
                self.writer.flush()
            self.sess.run(self.train_step, feed_dict={self.x: batch[0], self.y_: batch[1], self.keep_prob: 0.5})

    def test(self, mnist):
        acc_result = self.accuracy.eval(session=self.sess, feed_dict={
            self.x: mnist.test.images, self.y_: mnist.test.labels, self.keep_prob: 1.0})
        print(datetime.now().isoformat(), 'test accuracy %g' % acc_result)
        return acc_result

def removeFileInDir(targetDir): 
    for file in os.listdir(targetDir): 
        targetFile = os.path.join(targetDir,  file) 
        if os.path.isfile(targetFile):
            print 'Delete Old Log FIle:', targetFile
            os.remove(targetFile)

